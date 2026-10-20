import os
import requests
from flask import Flask, request

app = Flask(__name__)

GROUPME_BOT_ID = os.environ.get("GROUPME_BOT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "GroupMe AI bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    message = request.get_json(silent=True)

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

    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "contents": [{
                    "parts": [{"text": question}]
                }]
            },
            timeout=40,
        )

        if response.ok:
            data = response.json()
            answer = "".join(
                part.get("text", "")
                for candidate in data.get("candidates", [])
                for part in candidate.get("content", {}).get("parts", [])
            )
            if not answer:
                answer = "Sorry, the AI returned no text."
        else:
            answer = (
                f"Gemini error {response.status_code}: "
                f"{response.text[:250]}"
            )

    except requests.RequestException:
        answer = "Sorry, I couldn't connect to the AI service."

    try:
        requests.post(
            "https://api.groupme.com/v3/bots/post",
            json={
                "bot_id": GROUPME_BOT_ID,
                "text": answer[:900],
            },
            timeout=15,
        )
    except requests.RequestException:
        pass

    return "OK", 200

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
