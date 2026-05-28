from flask import Flask, render_template_string, request, jsonify
import subprocess
import threading
import os

app = Flask(__name__)

# Global log store
campaign_logs = []
campaign_running = False

html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Outreach AI</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',sans-serif;}
body{
    min-height:100vh;overflow:hidden;
    background:radial-gradient(circle at top left,#2563eb22,transparent 30%),
    radial-gradient(circle at bottom right,#7c3aed22,transparent 30%),#020617;
    display:flex;justify-content:center;align-items:center;color:white;
}
.bg-blur1,.bg-blur2{position:absolute;border-radius:50%;filter:blur(120px);opacity:0.4;}
.bg-blur1{width:300px;height:300px;background:#2563eb;top:-80px;left:-80px;}
.bg-blur2{width:280px;height:280px;background:#7c3aed;bottom:-100px;right:-100px;}
.card{
    position:relative;width:760px;padding:45px;border-radius:32px;
    background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);
    backdrop-filter:blur(24px);box-shadow:0 10px 40px rgba(0,0,0,0.45);
    animation:fadeIn 1s ease;
}
@keyframes fadeIn{from{opacity:0;transform:translateY(25px);}to{opacity:1;transform:translateY(0);}}
.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:35px;}
.logo{
    font-size:30px;font-weight:700;
    background:linear-gradient(90deg,#60a5fa,#a78bfa);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.status{padding:10px 18px;border-radius:999px;background:#10b98122;color:#6ee7b7;font-size:13px;}
.status.running{background:#f59e0b22;color:#fcd34d;}
label{display:block;margin-bottom:10px;color:#cbd5e1;font-size:14px;}
input{
    width:100%;padding:18px;border:none;border-radius:18px;
    background:#0f172a;color:white;margin-bottom:24px;outline:none;
    font-size:15px;transition:0.3s;
}
input:focus{box-shadow:0 0 0 2px #3b82f6;}
button{
    width:100%;padding:18px;border:none;border-radius:20px;
    background:linear-gradient(135deg,#2563eb,#7c3aed);
    color:white;font-size:16px;font-weight:600;cursor:pointer;transition:0.3s;
}
button:hover{transform:translateY(-3px);box-shadow:0 15px 35px rgba(99,102,241,0.4);}
button:disabled{opacity:0.5;cursor:not-allowed;transform:none;}
.logs{
    margin-top:28px;background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.06);border-radius:24px;
    padding:24px;height:220px;overflow:auto;
}
.logs pre{color:#cbd5e1;white-space:pre-wrap;font-size:13px;}
</style>
</head>
<body>
<div class="bg-blur1"></div>
<div class="bg-blur2"></div>
<div class="card">
    <div class="topbar">
        <div class="logo">OutreachAI</div>
        <div class="status" id="statusBadge">System Active</div>
    </div>

    <label>Target Clients</label>
    <input type="text" id="clients" placeholder="restaurants in new york" required>

    <label>Your Service</label>
    <input type="text" id="service" placeholder="SEO / Web Dev / AI Automation" required>

    <button id="launchBtn" onclick="launchCampaign()">Launch Campaign</button>

    <div class="logs">
        <pre id="logBox">Waiting for campaign start...</pre>
    </div>
</div>

<script>
let polling = null;

async function launchCampaign() {
    const clients = document.getElementById('clients').value.trim();
    const service = document.getElementById('service').value.trim();

    if (!clients || !service) return;

    document.getElementById('launchBtn').disabled = true;
    document.getElementById('statusBadge').textContent = 'Running...';
    document.getElementById('statusBadge').className = 'status running';
    document.getElementById('logBox').textContent = 'Launching campaign...\n';

    await fetch('/launch', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({clients, service})
    });

    // Start polling logs every 3 seconds
    polling = setInterval(fetchLogs, 3000);
}

async function fetchLogs() {
    const res = await fetch('/logs');
    const data = await res.json();

    const logBox = document.getElementById('logBox');
    logBox.textContent = data.logs;
    logBox.parentElement.scrollTop = logBox.parentElement.scrollHeight;

    if (!data.running) {
        clearInterval(polling);
        document.getElementById('launchBtn').disabled = false;
        document.getElementById('statusBadge').textContent = 'System Active';
        document.getElementById('statusBadge').className = 'status';
    }
}
</script>
</body>
</html>
"""

def run_campaign(target_clients, service):
    global campaign_logs, campaign_running
    campaign_logs = []
    campaign_running = True

    try:
        process = subprocess.Popen(
            ["python3", "agent.py", target_clients, service],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        # Stream logs line by line
        for line in process.stdout:
            campaign_logs.append(line.rstrip())
            print(line.rstrip())

        process.wait()
        campaign_logs.append("\n✅ Campaign Finished!")

    except Exception as e:
        campaign_logs.append(f"Error: {str(e)}")

    campaign_running = False


@app.route("/", methods=["GET"])
def home():
    return render_template_string(html)


@app.route("/launch", methods=["POST"])
def launch():
    global campaign_running

    if campaign_running:
        return jsonify({"status": "already running"})

    data = request.get_json()
    target_clients = data.get("clients", "")
    service = data.get("service", "")

    # Run in background thread
    thread = threading.Thread(
        target=run_campaign,
        args=(target_clients, service),
        daemon=True
    )
    thread.start()

    return jsonify({"status": "started"})


@app.route("/logs", methods=["GET"])
def logs():
    return jsonify({
        "logs": "\n".join(campaign_logs) if campaign_logs else "Starting...",
        "running": campaign_running
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)