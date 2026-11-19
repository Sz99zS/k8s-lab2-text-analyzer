"""AI Text Analyzer - backend (REST API).

Приймає текст, рахує статистику та визначає тональність (позитив/негатив/нейтрально)
за простим словником. Кожен запит записується в лог-файл, який читає контейнер log-agent.
"""
import logging
import os
import re
from collections import Counter

from flask import Flask, jsonify, request

LOG_DIR = os.environ.get("LOG_DIR", "/var/log/app")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [api] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log")),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("api")
# Вимикаємо службові логи веб-сервера, щоб у файлі були лише події додатку
logging.getLogger("werkzeug").setLevel(logging.ERROR)

POSITIVE = {
    "good", "great", "excellent", "happy", "love", "like", "nice", "best", "cool", "awesome",
    "добре", "добрий", "чудово", "чудовий", "гарний", "люблю", "подобається", "супер", "класно", "радий",
    "хорошо", "хороший", "отлично", "нравится", "круто",
}
NEGATIVE = {
    "bad", "terrible", "awful", "sad", "hate", "worst", "poor", "angry", "boring", "ugly",
    "погано", "поганий", "жахливо", "сумно", "ненавиджу", "нудно", "злий", "гірший",
    "плохо", "плохой", "ужасно", "грустно", "ненавижу", "скучно",
}

app = Flask(__name__)


def analyze(text: str) -> dict:
    words = re.findall(r"[\w']+", text.lower())
    pos = sum(1 for w in words if w in POSITIVE)
    neg = sum(1 for w in words if w in NEGATIVE)
    if pos > neg:
        sentiment = "positive"
    elif neg > pos:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    top = Counter(w for w in words if len(w) > 3).most_common(5)
    return {
        "characters": len(text),
        "words": len(words),
        "sentences": len(sentences),
        "positive_words": pos,
        "negative_words": neg,
        "sentiment": sentiment,
        "top_words": [{"word": w, "count": c} for w, c in top],
    }


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.post("/api/analyze")
def analyze_endpoint():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()
    if not text:
        log.warning("empty text received")
        return jsonify(error="text is empty"), 400
    result = analyze(text)
    log.info("analyzed text: words=%d sentiment=%s", result["words"], result["sentiment"])
    return jsonify(result)


if __name__ == "__main__":
    log.info("AI Text Analyzer API started on port 5000")
    app.run(host="0.0.0.0", port=5000)
