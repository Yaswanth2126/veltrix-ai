import google.generativeai as genai
import os
from flask import Flask, render_template, request, redirect, session, jsonify
import random
import requests

genai.configure(api_key=os.getenv("AIzaSyBYyJ-x5zq6YG1zB1IqQhmjLM01eb11ZSU"))

model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

app.secret_key = "veltrix_secret_key"

BOT_TOKEN = "8733303340:AAHnK9V2BNCkTYk2zheSz4iwL8O9xdvN89E"
CHAT_ID = "8425128703"

USERNAME = "admin"
PASSWORD = "veltrix123"

# ======================================
# LOGIN
# ======================================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:

            session["user"] = username

            return redirect("/dashboard")

    return render_template("login.html")

# ======================================
# DASHBOARD
# ======================================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form.get("message")

    response = model.generate_content(user_message)

    return {
        "reply": response.text
    }

# ======================================
# MARKET DATA
# ======================================

@app.route("/market-data")
def market_data():

    data = {

        "market": random.choice([
            "BULLISH",
            "BEARISH",
            "SIDEWAYS"
        ]),

        "portfolio": random.randint(
            4000000,
            6000000
        ),

        "positions": random.randint(
            10,
            35
        ),

        "winrate": random.randint(
            80,
            95
        ),

        "pnl": random.randint(
            50000,
            200000
        ),

        "signals": [

            {
                "stock":"RELIANCE",
                "signal":"BUY",
                "confidence":92
            },

            {
                "stock":"TCS",
                "signal":"SELL",
                "confidence":88
            }

        ],

        "watchlist":[

            {
                "name":"RELIANCE",
                "price":2942
            },

            {
                "name":"TCS",
                "price":4026
            },

            {
                "name":"INFY",
                "price":1486
            }

        ],

        "trades":[]

    }

    return jsonify(data)

# ======================================
# TELEGRAM ALERT
# ======================================

@app.route("/send-alert")
def send_alert():

    message = """
🚀 VELTRIX AI ALERT

📈 BUY SIGNAL: RELIANCE

🔥 Confidence: 92%
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {

        "chat_id": CHAT_ID,

        "text": message

    }

    requests.post(url, data=payload)

    return {"status":"alert sent"}

# ======================================
# LOGOUT
# ======================================

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")

# ======================================
# RUN APP
# ======================================

if __name__ == "__main__":
    app.run(debug=True)