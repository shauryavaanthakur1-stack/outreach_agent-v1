from flask import Flask, render_template_string, request, jsonify
import os
import json

app = Flask(__name__)

# FILE TO STORE LATEST TASK
TASK_FILE = "task.json"

html = """

<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>OutreachAI</title>

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

.bg1,
.bg2{

    position:absolute;

    border-radius:50%;

    filter:blur(120px);

    opacity:0.4;
}

.bg1{

    width:300px;
    height:300px;

    background:#2563eb;

    top:-80px;
    left:-80px;
}

.bg2{

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
}

.logs{

    margin-top:28px;

    background:
    rgba(255,255,255,0.04);

    border:
    1px solid rgba(255,255,255,0.06);

    border-radius:24px;

    padding:24px;

    height:220px;

    overflow:auto;
}

.logs pre{

    color:#cbd5e1;

    white-space:pre-wrap;

    font-size:13px;
}

</style>

</head>

<body>

<div class="bg1"></div>
<div class="bg2"></div>

<div class="card">

<div class="topbar">

<div class="logo">
OutreachAI
</div>

<div class="status">
Online
</div>

</div>

<label>
Target Clients
</label>

<input
type="text"
id="clients"
placeholder="dentists in london"
>

<label>
Your Service
</label>

<input
type="text"
id="service"
placeholder="seo / ai automation"
>

<button onclick="launchCampaign()">
Launch Campaign
</button>

<div class="logs">

<pre id="logs">

Waiting for campaign...

</pre>

</div>

</div>

<script>

async function launchCampaign(){

    const clients =
    document.getElementById(
        "clients"
    ).value;

    const service =
    document.getElementById(
        "service"
    ).value;

    if(!clients || !service){
        return;
    }

    const response = await fetch(
        "/launch",
        {
            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                clients,
                service
            })
        }
    );

    const data = await response.json();

    document.getElementById(
        "logs"
    ).textContent = data.message;
}

</script>

</body>

</html>

"""

@app.route("/")
def home():

    return render_template_string(
        html
    )

@app.route(
    "/launch",
    methods=["POST"]
)
def launch():

    data = request.get_json()

    clients = data.get(
        "clients"
    )

    service = data.get(
        "service"
    )

    task_data = {

        "clients": clients,

        "service": service,

        "status": "pending"
    }

    with open(
        TASK_FILE,
        "w"
    ) as f:

        json.dump(
            task_data,
            f
        )

    print(
        "\nNew Campaign Received\n"
    )

    print(task_data)

    return jsonify({

        "message": f"""

Campaign Sent Successfully

Target Clients:
{clients}

Service:
{service}

Your PC listener will execute this automatically.

"""
    })

@app.route("/task")
def get_task():

    if not os.path.exists(
        TASK_FILE
    ):

        return jsonify({
            "status":"none"
        })

    with open(
        TASK_FILE,
        "r"
    ) as f:

        data = json.load(f)

    return jsonify(data)

@app.route(
    "/complete",
    methods=["POST"]
)
def complete():

    if os.path.exists(
        TASK_FILE
    ):

        os.remove(
            TASK_FILE
        )

    return jsonify({
        "status":"completed"
    })

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )