import os
import requests
from flask import Flask, request

app = Flask(__name__)

GROUPME_BOT_ID = os.environ.get("GROUPME_BOT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "GroupMe AI bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    message = request.json

    if not message:
        return "OK", 200

    text = message.get("text", "")
    sender = message.get("sender_type", "")
    bot_id = message.get("bot_id", "")

    if sender == "bot" or bot_id == GROUPME_BOT_ID:
        return "OK", 200

    if not text.lower().startswith("ai:"):
        return "OK", 200

    question = text[3:].strip()

    if not question:
        return "OK", 200

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4.1-mini",
            "input": question,
        },
        timeout=30,
    )

    if response.ok:
        data = response.json()
        answer = "".join(
            item.get("text", "")
            for item in data.get("output", [])
            if item.get("type") == "message"
            for item in item.get("content", [])
            if item.get("type") == "output_text"
        )
    else:
        answer = "Sorry, I couldn't reach the AI service."

    requests.post(
        "https://api.groupme.com/v3/bots/post",
        json={
            "bot_id": GROUPME_BOT_ID,
            "text": answer[:900],
        },
        timeout=15,
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
