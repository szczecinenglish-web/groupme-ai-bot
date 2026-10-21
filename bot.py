
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
            "text": "yes we are working on that"
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
