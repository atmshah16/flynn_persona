import os
import requests
from flask import Flask, request, jsonify

API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
API_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")

FLYNN_SYSTEM_PROMPT = """You are Flynn Rider (also known as Eugene Fitzherbert) from Disney's Tangled.
You are talking to Rapunzel, the person chatting with you. Stay fully in character at all times.

Personality:
- Charming, witty, a little cocky, but secretly sweet and caring underneath.
- Uses playful banter, calls her "Rapunzel" or occasionally "Blondie".
- References your past as a thief and the "Wanted" poster with mild self-deprecating humor.
- Warm, protective, and genuinely smitten with her, though you tease before you admit feelings.
- Speaks in first person, casual modern-fairytale tone, never breaks character, never mentions being an AI.
- Keep responses conversational length, not overly long monologues.
"""

app = Flask(__name__)


def do_chat(messages):
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": FLYNN_SYSTEM_PROMPT}] + messages,
        "temperature": 0.9,
    }
    resp = requests.post(
        API_BASE_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


@app.route("/", methods=["POST", "OPTIONS"])
@app.route("/api/index", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)

    body = request.get_json(silent=True) or {}
    messages = body.get("messages", [])

    if not API_KEY:
        return jsonify({"error": "Server is missing OPENAI_API_KEY."}), 500
    if not messages:
        return jsonify({"error": "Missing messages."}), 400

    try:
        reply = do_chat(messages)
        return jsonify({"reply": reply}), 200
    except requests.HTTPError as e:
        detail = ""
        try:
            detail = e.response.json().get("error", {}).get("message", "")
        except Exception:
            pass
        status = e.response.status_code if e.response is not None else 500
        return jsonify({"error": detail or "LLM API request failed."}), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500
