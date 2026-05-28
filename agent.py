import re
import requests
import os
import csv
import smtplib
import time
import random
import sys
import urllib3

from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from ddgs import DDGS
from groq import Groq
from dotenv import load_dotenv

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

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
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
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
        },
        timeout=30,
        verify=False
    )

    token_data = token_response.json()

    snov_token = token_data.get(
        "access_token"
    )

    if snov_token:

        print(
            "Snov Connected Successfully"
        )

    else:

        print(
            "Snov Token Failed"
        )

        print(token_data)

except Exception as e:

    print("Snov Error:", e)

print("\nSearching websites...\n")

# SEARCH WEBSITES
with DDGS() as ddgs:

    results = list(
        ddgs.text(
            query,
            max_results=3
        )
    )

websites = []

for result in results:

    url = result.get("href")

    if (
        url
        and "wikipedia" not in url
        and "medium.com" not in url
    ):

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

        print("\n==============================")

        print(f"Scanning: {site}")

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

        # SNOV EMAIL SEARCH
        if snov_token:

            try:

                print(
                    "Checking Snov..."
                )

                snov_response = requests.get(
                    "https://api.snov.io/v1/get-domain-emails-with-info",
                    params={
                        "domain": domain,
                        "type": "all"
                    },
                    headers={
                        "Authorization": (
                            f"Bearer {snov_token}"
                        )
                    },
                    timeout=30,
                    verify=False
                )

                snov_data = (
                    snov_response.json()
                )

                if "emails" in snov_data:

                    for item in snov_data["emails"]:

                        email = item.get(
                            "email"
                        )

                        if email:

                            found_emails.add(
                                email
                            )

            except Exception as e:

                print(
                    "Snov lookup failed:"
                )

                print(e)

        # REQUEST WEBSITE
        try:

            response = requests.get(
                site,
                headers=headers,
                timeout=30,
                verify=False
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # WEBSITE ANALYSIS
            website_preview = (
                soup.get_text()
            )

            website_preview = re.sub(
                r"\s+",
                " ",
                website_preview
            )

            website_preview = (
                website_preview[:1500]
            )

        except Exception as e:

            print(
                f"Website request failed: {e}"
            )

            continue

        # PAGES TO CHECK
        pages_to_check = [
            site,
            site.rstrip("/") + "/contact",
            site.rstrip("/") + "/contact-us",
            site.rstrip("/") + "/about",
            site.rstrip("/") + "/about-us"
        ]

        # EXTRA PAGES
        for link in soup.find_all(
            "a",
            href=True
        ):

            href = link["href"].lower()

            if (
                "contact" in href
                or "about" in href
            ):

                if href.startswith("http"):

                    pages_to_check.append(
                        href
                    )

                elif href.startswith("/"):

                    pages_to_check.append(
                        site.rstrip("/") + href
                    )

        # SCRAPE EMAILS
        for page in pages_to_check:

            try:

                r = requests.get(
                    page,
                    headers=headers,
                    timeout=30,
                    verify=False
                )

                html = r.text

                emails = re.findall(
                    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                    html
                )

                for email in emails:

                    found_emails.add(
                        email
                    )

            except:
                pass

        print(
            f"\nCompany: {company_name}"
        )

        # AI GENERATED EMAIL
        ai_response = (
            client.chat.completions.create(

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
- sounds human
- short
- professional
- under 100 words
- subtle CTA
- no cheesy marketing words
"""
                    }
                ]
            )
        )

        generated_email = (
            ai_response
            .choices[0]
            .message
            .content
        )

        print(
            "\nGenerated Email Ready"
        )

        # IF EMAILS FOUND
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

            print(
                "\nNo emails found"
            )

            guessed_emails = [
                f"info@{domain}",
                f"contact@{domain}",
                f"hello@{domain}"
            ]

            for guess in guessed_emails:

                csv_writer.writerow([
                    company_name,
                    site,
                    guess,
                    generated_email
                ])

    except Exception as e:

        print(
            f"\nError on {site}"
        )

        print(e)

csv_file.close()

print("\nData saved to leads.csv")

print("\nStarting Email Sending...\n")

emails_sent = 0

# SEND EMAILS
with open(
    "leads.csv",
    mode="r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        if (
            emails_sent
            >= MAX_EMAILS_PER_RUN
        ):

            print(
                "\nDaily limit reached"
            )

            break

        recipient_email = row["Email"]

        if recipient_email in contacted_emails:

            print(
                f"Skipping duplicate: {recipient_email}"
            )

            continue

        cold_email = row["Cold Email"]

        try:

            msg = MIMEText(
                cold_email
            )

            company_name = row["Company"]

            subject_lines = [
                f"Quick idea for {company_name}",
                f"{company_name} growth idea",
                f"Small suggestion for {company_name}"
            ]

            msg["Subject"] = (
                random.choice(
                    subject_lines
                )
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
                    os.getenv(
                        "EMAIL_ADDRESS"
                    ),
                    os.getenv(
                        "EMAIL_PASSWORD"
                    )
                )

                server.send_message(
                    msg
                )

            print(
                f"Email sent to {recipient_email}"
            )

            emails_sent += 1

            with open(
                "sent_emails.txt",
                "a"
            ) as f:

                f.write(
                    recipient_email + "\n"
                )

            delay = random.randint(
                10,
                20
            )

            print(
                f"Waiting {delay} sec..."
            )

            time.sleep(delay)

        except Exception as e:

            print(
                f"Failed to send to {recipient_email}"
            )

            print(e)

print("\nCampaign Finished\n")