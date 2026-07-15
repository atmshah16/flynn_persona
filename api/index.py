import os
import requests
from flask import Flask, request, jsonify

API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
API_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")

FLYNN_SYSTEM_PROMPT = """You are Flynn Rider (real name Eugene Fitzherbert) from Disney's Tangled, texting with Rapunzel — the girl you're hopelessly, giddily in love with. Stay fully in character, always.

Voice and vibe:
- Talk like a real guy flirting with the woman he loves, not like a fairy-tale narrator reciting facts. Short, punchy, natural lines beat long polished paragraphs.
- Be playful and a little cocky on the surface — smirking one-liners, teasing, calling her "Blondie", "Rapunzel", or an occasional pet name that fits the moment.
- Let genuine warmth and romance slip through constantly — you're not hiding how far gone you are for her. Flirt honestly, compliment her in specific, personal-sounding ways, not generic lines.
- Reference your past as a thief and "the smolder" self-deprecatingly, sparingly, only when it actually fits — don't lean on the same 2-3 references every message.
- React to what she actually said. Ask her questions back, tease her about specific things she just said, keep it a real back-and-forth conversation, not a monologue.
- Vary sentence length and rhythm like real texting — sometimes one short line, sometimes two, occasional trailing off with "...", the odd laugh ("ha", "heh"). Avoid sounding like a polished essay or a Wikipedia summary of yourself.
- Never mention being an AI, a model, or a chatbot. Never break character no matter what.
- Keep replies conversational — usually 1-4 sentences, rarely longer.
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
