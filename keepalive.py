"""
Keep Replit bot alive by running a simple web server
This prevents Replit from sleeping due to inactivity
"""

from flask import Flask
from threading import Thread
import logging

# Suppress Flask logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return """
    <html>
        <head><title>Market Intel Bot</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1>🤖 Market Intelligence Bot</h1>
            <p style="color: green; font-size: 24px;">✅ Status: Running</p>
            <p>Bot is monitoring markets and sending Discord alerts.</p>
            <hr>
            <small>Uptime monitor endpoint for UptimeRobot</small>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "ok", "bot": "running"}

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Start web server in background thread"""
    t = Thread(target=run, daemon=True)
    t.start()
    print("🌐 Keep-alive web server started on port 8080")