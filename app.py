from flask import Flask, render_template_string, request
import subprocess

app = Flask(__name__)

html = """

<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>AI Outreach AI</title>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:'Inter',sans-serif;
}

body{

    min-height:100vh;

    overflow:hidden;

    background:
    radial-gradient(circle at top left,#2563eb22,transparent 30%),
    radial-gradient(circle at bottom right,#7c3aed22,transparent 30%),
    #020617;

    display:flex;
    justify-content:center;
    align-items:center;

    color:white;
}

.bg-blur1,
.bg-blur2{

    position:absolute;

    border-radius:50%;

    filter:blur(120px);

    opacity:0.4;
}

.bg-blur1{

    width:300px;
    height:300px;

    background:#2563eb;

    top:-80px;
    left:-80px;
}

.bg-blur2{

    width:280px;
    height:280px;

    background:#7c3aed;

    bottom:-100px;
    right:-100px;
}

.card{

    position:relative;

    width:760px;

    padding:45px;

    border-radius:32px;

    background:
    rgba(255,255,255,0.05);

    border:
    1px solid rgba(255,255,255,0.08);

    backdrop-filter:blur(24px);

    box-shadow:
    0 10px 40px rgba(0,0,0,0.45);

    animation:fadeIn 1s ease;
}

@keyframes fadeIn{

    from{
        opacity:0;
        transform:translateY(25px);
    }

    to{
        opacity:1;
        transform:translateY(0);
    }
}

.topbar{

    display:flex;
    justify-content:space-between;
    align-items:center;

    margin-bottom:35px;
}

.logo{

    font-size:30px;
    font-weight:700;

    background:
    linear-gradient(
        90deg,
        #60a5fa,
        #a78bfa
    );

    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.status{

    padding:10px 18px;

    border-radius:999px;

    background:#10b98122;

    color:#6ee7b7;

    font-size:13px;
}

label{

    display:block;

    margin-bottom:10px;

    color:#cbd5e1;

    font-size:14px;
}

input{

    width:100%;

    padding:18px;

    border:none;

    border-radius:18px;

    background:#0f172a;

    color:white;

    margin-bottom:24px;

    outline:none;

    font-size:15px;

    transition:0.3s;
}

input:focus{

    box-shadow:
    0 0 0 2px #3b82f6;
}

button{

    width:100%;

    padding:18px;

    border:none;

    border-radius:20px;

    background:
    linear-gradient(
        135deg,
        #2563eb,
        #7c3aed
    );

    color:white;

    font-size:16px;

    font-weight:600;

    cursor:pointer;

    transition:0.3s;
}

button:hover{

    transform:translateY(-3px);

    box-shadow:
    0 15px 35px rgba(99,102,241,0.4);
}

.stats{

    margin-top:32px;

    display:grid;

    grid-template-columns:
    repeat(3,1fr);

    gap:18px;
}

.stat{

    background:
    rgba(255,255,255,0.04);

    border:
    1px solid rgba(255,255,255,0.06);

    border-radius:24px;

    padding:24px;

    transition:0.3s;
}

.stat:hover{

    transform:translateY(-4px);
}

.stat h2{

    font-size:34px;

    margin-bottom:8px;
}

.stat p{

    color:#94a3b8;
}

.logs{

    margin-top:28px;

    background:
    rgba(255,255,255,0.04);

    border:
    1px solid rgba(255,255,255,0.06);

    border-radius:24px;

    padding:24px;

    height:180px;

    overflow:auto;
}

.logs p{

    color:#cbd5e1;

    margin-bottom:12px;
}

</style>

</head>

<body>

<div class="bg-blur1"></div>
<div class="bg-blur2"></div>

<div class="card">

<div class="topbar">

<div class="logo">
OutreachAI
</div>

<div class="status">
System Active
</div>

</div>

<form method="POST">

<label>
Target Clients
</label>

<input
type="text"
name="clients"
placeholder="dentists in london"
required
>

<label>
Your Service
</label>

<input
type="text"
name="service"
placeholder="SEO / Web Dev / AI Automation"
required
>

<button type="submit">
Launch Campaign
</button>

</form>

<div class="stats">

<div class="stat">

<h2>24</h2>

<p>Leads Found</p>

</div>

<div class="stat">

<h2>10</h2>

<p>Emails Sent</p>

</div>

<div class="stat">

<h2>3</h2>

<p>Replies</p>

</div>

</div>

<div class="logs">

<p>✓ AI engine initialized</p>

<p>✓ Waiting for campaign start...</p>

<p>✓ Personalized outreach system active</p>

</div>

</div>

</body>

</html>

"""

@app.route("/", methods=["GET", "POST"])

def home():

    if request.method == "POST":

        target_clients = request.form.get(
            "clients"
        )

        service = request.form.get(
            "service"
        )

        print("\nLaunching Campaign...\n")

        print("Target Clients:", target_clients)

        print("Service:", service)

        subprocess.Popen(
            [
                r"C:\Users\Eklavya\ai_agent\venv\Scripts\python.exe",
                "agent.py",
                target_clients,
                service
            ]
        )

    return render_template_string(html)

if __name__ == "__main__":

    import os

port = int(
    os.environ.get("PORT", 5000)
)

app.run(
    host="0.0.0.0",
    port=port
)