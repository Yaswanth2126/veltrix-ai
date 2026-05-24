from flask import Flask, render_template, request, redirect, url_for
import google.generativeai as genai
import os

app = Flask(__name__)

# Gemini AI Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

# Login Page
@app.route("/")
def login():
    return render_template("login.html")

# Dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

# AI Chat Route
@app.route("/chat", methods=["POST"])
def chat():

    try:
        user_message = request.form.get("message")

        response = model.generate_content(user_message)

        return {
            "reply": response.text
        }

    except Exception as e:

        return {
            "reply": str(e)
        }

# Run App
if __name__ == "__main__":
    app.run(debug=True)