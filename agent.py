import re
import requests
import os
import csv
import smtplib
import json
import time
import random
import sys

from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from ddgs import DDGS
from groq import Groq
from dotenv import load_dotenv

# LOAD ENV VARIABLES
load_dotenv()

# API KEYS
groq_api_key = os.getenv("GROQ_API_KEY")

snov_client_id = os.getenv("SNOV_CLIENT_ID")
snov_client_secret = os.getenv("SNOV_CLIENT_SECRET")

# GROQ CLIENT
client = Groq(
    api_key=groq_api_key
)

# GET INPUTS FROM DASHBOARD
query = sys.argv[1]

service = sys.argv[2]

# DAILY LIMIT
MAX_EMAILS_PER_RUN = 10

# HEADERS
headers = {
    "User-Agent": "Mozilla/5.0"
}

# GET SNOV TOKEN
print("\nConnecting Snov API...\n")

snov_token = None

try:

    token_response = requests.post(
        "https://api.snov.io/v1/oauth/access_token",
        data={
            "grant_type": "client_credentials",
            "client_id": snov_client_id,
            "client_secret": snov_client_secret
        }
    )

    token_data = token_response.json()

    snov_token = token_data.get("access_token")

    if snov_token:

        print("Snov Connected Successfully")

    else:

        print("Snov Token Failed")
        print(token_data)

except Exception as e:

    print("Snov Error:", e)

print("\nSearching websites...\n")

# SEARCH WEBSITES
with DDGS() as ddgs:

    results = list(
        ddgs.text(
            query,
            max_results=5
        )
    )

websites = []

for result in results:

    url = result.get("href")

    if url:

        websites.append(url)

        print(url)

print("\nGenerating AI Emails...\n")

# ALREADY CONTACTED
contacted_emails = set()

if os.path.exists("sent_emails.txt"):

    with open(
        "sent_emails.txt",
        "r"
    ) as f:

        for line in f:

            contacted_emails.add(
                line.strip()
            )

# CREATE CSV FILE
csv_file = open(
    "leads.csv",
    mode="w",
    newline="",
    encoding="utf-8"
)

csv_writer = csv.writer(csv_file)

csv_writer.writerow([
    "Company",
    "Website",
    "Email",
    "Cold Email"
])

# LOOP THROUGH WEBSITES
for site in websites:

    try:

        # COMPANY NAME
        company_name = site.replace(
            "https://",
            ""
        ).replace(
            "http://",
            ""
        ).split("/")[0]

        domain = company_name

        found_emails = set()

        website_preview = ""

        # TRY SNOV API FIRST
        if snov_token:

            try:

                snov_response = requests.get(
                    "https://api.snov.io/v1/get-domain-emails-with-info",
                    params={
                        "domain": domain,
                        "type": "all"
                    },
                    headers={
                        "Authorization": f"Bearer {snov_token}"
                    }
                )

                snov_data = snov_response.json()

                if "emails" in snov_data:

                    for item in snov_data["emails"]:

                        email = item.get("email")

                        if email:

                            found_emails.add(email)

            except:
                pass

        # REQUEST WEBSITE
        response = requests.get(
            site,
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # WEBSITE ANALYSIS
        website_preview = soup.get_text()

        website_preview = re.sub(
            r"\s+",
            " ",
            website_preview
        )

        website_preview = website_preview[:2000]

        # PAGES TO CHECK
        pages_to_check = [
            site,
            site.rstrip("/") + "/contact",
            site.rstrip("/") + "/contact-us",
            site.rstrip("/") + "/about",
            site.rstrip("/") + "/about-us"
        ]

        # FIND EXTRA PAGES
        for link in soup.find_all("a", href=True):

            href = link["href"].lower()

            if (
                "contact" in href
                or "about" in href
                or "team" in href
                or "staff" in href
            ):

                if href.startswith("http"):

                    pages_to_check.append(href)

                elif href.startswith("/"):

                    pages_to_check.append(
                        site.rstrip("/") + href
                    )

        # SCRAPE EXTRA EMAILS
        for page in pages_to_check:

            try:

                r = requests.get(
                    page,
                    headers=headers,
                    timeout=10
                )

                html = r.text

                emails = re.findall(
                    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                    html
                )

                for email in emails:

                    found_emails.add(email)

                soup2 = BeautifulSoup(
                    html,
                    "html.parser"
                )

                for a in soup2.find_all("a", href=True):

                    if "mailto:" in a["href"]:

                        mail = a["href"].replace(
                            "mailto:",
                            ""
                        ).split("?")[0]

                        found_emails.add(mail)

            except:
                pass

        print("\n==============================")
        print(f"Company: {company_name}")

        # AI GENERATED EMAIL
        ai_response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": f"""
You are writing a highly personalized cold email.

Target company:
{company_name}

Website information:
{website_preview}

My service:
{service}

Write a personalized cold email that:
- mentions something specific about their business
- sounds human
- is professional
- is short
- avoids sounding spammy
- under 120 words
- includes a subtle CTA

Do not use cheesy marketing language.
"""
                }
            ]
        )

        generated_email = (
            ai_response
            .choices[0]
            .message
            .content
        )

        print("\nGenerated Cold Email:\n")

        print(generated_email)

        # PRINT FOUND EMAILS
        if found_emails:

            print("\nEmails Found:\n")

            for email in found_emails:

                print(email)

                csv_writer.writerow([
                    company_name,
                    site,
                    email,
                    generated_email
                ])

        else:

            print("\nNo emails found")

            guessed_emails = [
                f"info@{company_name}",
                f"contact@{company_name}",
                f"hello@{company_name}"
            ]

            for guess in guessed_emails:

                print(guess)

                csv_writer.writerow([
                    company_name,
                    site,
                    guess,
                    generated_email
                ])

    except Exception as e:

        print(f"\nError on {site}")
        print(e)

# CLOSE CSV
csv_file.close()

print("\nData saved to leads.csv")

print("\nStarting Email Sending...\n")

emails_sent = 0

# READ CSV
with open(
    "leads.csv",
    mode="r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        if emails_sent >= MAX_EMAILS_PER_RUN:

            print("\nDaily limit reached")
            break

        recipient_email = row["Email"]

        # SKIP DUPLICATE EMAILS
        if recipient_email in contacted_emails:

            print(
                f"Skipping duplicate: {recipient_email}"
            )

            continue

        cold_email = row["Cold Email"]

        try:

            msg = MIMEText(cold_email)

            # RANDOM SUBJECTS
            subject_lines = [
                f"Quick idea for {company_name}",
                f"{company_name} growth idea",
                f"Question about your business",
                f"Small suggestion for {company_name}",
                f"Potential improvement for your website"
            ]

            msg["Subject"] = random.choice(
                subject_lines
            )

            msg["From"] = os.getenv(
                "EMAIL_ADDRESS"
            )

            msg["To"] = recipient_email

            with smtplib.SMTP_SSL(
                "smtp.gmail.com",
                465
            ) as server:

                server.login(
                    os.getenv("EMAIL_ADDRESS"),
                    os.getenv("EMAIL_PASSWORD")
                )

                server.send_message(msg)

            print(
                f"Email sent to {recipient_email}"
            )

            emails_sent += 1

            # SAVE SENT EMAIL
            with open(
                "sent_emails.txt",
                "a"
            ) as f:

                f.write(
                    recipient_email + "\n"
                )

            # RANDOM DELAY
            delay = random.randint(20, 60)

            print(
                f"Waiting {delay} seconds...\n"
            )

            time.sleep(delay)

        except Exception as e:

            print(
                f"Failed to send to {recipient_email}"
            )

            print(e)

print("\nCampaign Finished\n")