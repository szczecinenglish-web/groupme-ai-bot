
import os
import requests
from flask import Flask, request

app = Flask(__name__)

GROUPME_BOT_ID = os.environ["GROUPME_BOT_ID"]

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200

@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json(silent=True) or {}
    print("SENDER NAME:", data.get("name"))
    print("SENDER ID:", data.get("user_id"))

    # Ignore bot messages to prevent an endless reply loop
    if data.get("sender_type") == "bot":
        return "OK", 200

    # Ignore requests that aren't actual messages
    if not data.get("text"):
        return "OK", 200

    # Reply with the same text every time
    response = requests.post(
        "https://api.groupme.com/v3/bots/post",
        json={
            "bot_id": GROUPME_BOT_ID,
            "text": "It is important everyone in Church Hill is happy and safe. Your input is essential to the service we provide. Haze and Alex create conflict but they are good people at heart. I am a bot but I have a human's heart."
        },
        timeout=10
    )

    response.raise_for_status()
    return "OK", 200

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
