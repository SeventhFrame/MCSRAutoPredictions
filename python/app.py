import os
import threading
from urllib.parse import urlencode

from flask import Flask, jsonify, redirect, render_template, request
import requests
import bot

app = Flask(__name__)

TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_REDIRECT_URI = "http://localhost:3000/auth/callback"

bot_thread = None
access_token = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predictions", methods=["POST", "GET"])
def predictions():

    global bot_thread
    bot.stop_bot_check.set()
    if bot_thread is not None:
        bot_thread.join()

    name = request.form["username"]
    return render_template("predictions.html", name=name)

@app.route("/start", methods=["POST", "GET"])
def start():
    global bot_thread
    bot.stop_bot_check.clear()

    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=bot.start_bot)
        bot_thread.start()

    name = request.form.get("username", "")
    return render_template("start.html", name=name)

@app.route("/login")
def login():
    if not TWITCH_CLIENT_ID:
        return "TWITCH_CLIENT_ID is not configured", 500

    params = {
        "response_type": "token",
        "client_id": TWITCH_CLIENT_ID,
        "redirect_uri": TWITCH_REDIRECT_URI,
        "scope": "channel:manage:predictions channel:read:predictions",
    }
    authorize_url = "https://id.twitch.tv/oauth2/authorize?" + urlencode(params)
    return redirect(authorize_url)

@app.route("/auth/callback")
def auth_callback():
    return render_template("auth_callback.html")

@app.route("/auth/token", methods=["POST"])
def auth_token():
    global access_token

    token = request.json.get("access_token")
    if not token:
        return jsonify({"error": "missing access token"}), 400

    response = requests.get(
        "https://id.twitch.tv/oauth2/validate",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    if not response.ok:
        return jsonify({"error": "invalid access token"}), 401

    access_token = token
    print(access_token)
    return jsonify({"login": response.json().get("login")})

if __name__ == "__main__":
    app.run(port=3000)


    