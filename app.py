
import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
AI_API_KEY = os.environ["AI_API_KEY"]
AI_BASE_URL = os.environ["AI_BASE_URL"]
AI_MODEL = os.environ["AI_MODEL"]

ai = OpenAI(
    api_key=AI_API_KEY,
    base_url=AI_BASE_URL
)

@app.route("/", methods=["GET"])
def home():
    return "My AI Telegram bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id or not text:
        return {"ok": True}

    if text == "/start":
        answer = "Привет! 🤖 Я твой ИИ-собеседник!"
    else:
        try:
            result = ai.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты дружелюбный ИИ-собеседник. Отвечай по-русски."
                    },
                    {"role": "user", "content": text}
                ],
                max_tokens=500
            )
            answer = result.choices[0].message.content
            answer = answer or "Попробуй задать вопрос ещё раз."
        except Exception:
            answer = "Не получилось связаться с ИИ. Попробуй позже."

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": answer},
        timeout=20
    )
    return {"ok": True}

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000"))
    )
