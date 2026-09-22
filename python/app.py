import os
import threading
import webbrowser
from urllib.parse import urlencode

from flask import Flask, jsonify, redirect, render_template, request
import requests
import bot

app = Flask(__name__)

TWITCH_CLIENT_ID = "oo93hqbdqso4wgw0guen9rw21lg96f"
TWITCH_REDIRECT_URI = "http://localhost:3000/auth/callback"
APP_HOST = os.environ.get("AUTOPREDICTIONS_HOST", "127.0.0.1")
APP_PORT = int(os.environ.get("AUTOPREDICTIONS_PORT", "3000"))

bot_thread = None
access_token = None
broadcaster_id = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predictions", methods=["POST", "GET"])
def predictions():
    mcsr_name = request.form.get("mcsr_name", "").strip()

    if not mcsr_name:
        return render_template(
            "predictions.html",
            error="Please enter an MCSR username or ID.",
        ), 400

    try:
        response = requests.get(
            f"https://api.mcsrranked.com/users/{mcsr_name}/",
            timeout=5,
        )
        response_data = response.json()
    except (requests.RequestException, ValueError):
        return render_template(
            "predictions.html",
            mcsr_name=mcsr_name,
            error="The MCSR service could not be reached. Please try again.",
        ), 502

    if not response.ok or response_data.get("status") != "success":
        return render_template(
            "predictions.html",
            mcsr_name=mcsr_name,
            error="No matching MCSR username or ID was found.",
        ), 404

    try:
        mcsr_id = response_data["data"]["uuid"]
    except (KeyError, TypeError):
        return render_template(
            "predictions.html",
            mcsr_name=mcsr_name,
            error="The MCSR service returned an invalid user.",
        ), 502

    return render_template(
        "predictions.html",
        mcsr_name=mcsr_name,
        mcsr_id=mcsr_id,
        success=True,
    )

@app.route("/start", methods=["POST", "GET"])
def start():
    global bot_thread

    mcsr_id = request.form.get("mcsr_id", "").strip()
    if not mcsr_id:
        return "Missing MCSR user ID", 400
    if not access_token or not broadcaster_id:
        return "Please log in with Twitch before starting predictions", 401
    if bot_thread is not None and bot_thread.is_alive():
        return "Predictions are already running", 409

    bot.stop_bot_check.clear()

    bot_thread = threading.Thread(
        target=bot.start_bot,
        args=(mcsr_id, access_token, TWITCH_CLIENT_ID, broadcaster_id),
        daemon=True,
    )
    bot_thread.start()

    mcsr_name = request.form.get("mcsr_name", "")
    return render_template("start.html", mcsr_name=mcsr_name)

@app.route("/stop", methods=["POST"])
def stop():
    bot.stop_bot_check.set()

    stopped = True
    if bot_thread is not None and bot_thread.is_alive():
        bot_thread.join(timeout=10)
        stopped = not bot_thread.is_alive()

    return render_template(
        "start.html",
        mcsr_name=request.form.get("mcsr_name", ""),
        stopped=stopped,
    )

@app.route("/status")
def status():
    return jsonify({
        "status": bot.run_status,
        "message": bot.run_message,
    })

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
    global access_token, broadcaster_id

    access_token = None
    broadcaster_id = None

    token = (request.json or {}).get("access_token")
    if not isinstance(token, str) or not token:
        return jsonify({"error": "missing access token"}), 400

    try:
        response = requests.get(
            "https://id.twitch.tv/oauth2/validate",
            headers={
                "Authorization": f"OAuth {token}",
                "Client-Id": TWITCH_CLIENT_ID,
            },
            timeout=5,
        )
        validation_data = response.json()
    except (requests.RequestException, ValueError):
        return jsonify({"error": "could not validate access token"}), 502

    if not response.ok:
        return jsonify({"error": "invalid access token"}), 401

    if validation_data.get("client_id") != TWITCH_CLIENT_ID:
        return jsonify({"error": "access token belongs to another application"}), 401

    validated_broadcaster_id = validation_data.get("user_id")
    scopes = validation_data.get("scopes", [])
    if not validated_broadcaster_id:
        return jsonify({"error": "validated token has no Twitch user ID"}), 401
    if "channel:manage:predictions" not in scopes:
        return jsonify({"error": "token lacks prediction permissions"}), 403

    access_token = token
    broadcaster_id = validated_broadcaster_id
    return jsonify({
        "login": validation_data.get("login"),
        "broadcaster_id": broadcaster_id,
    })

@app.route("/mcsr-info", methods=["POST", "GET"])
def mcsr_info():
    return render_template("mcsr_info.html")


if __name__ == "__main__":
    browser_url = f"http://localhost:{APP_PORT}/"
    threading.Timer(1.0, webbrowser.open, args=(browser_url,)).start()
    app.run(
        host=APP_HOST,
        port=APP_PORT,
        debug=False,
        use_reloader=False,
    )


    