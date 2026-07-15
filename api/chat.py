import json
import os
import requests
from http.server import BaseHTTPRequestHandler

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


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")

            messages = body.get("messages", [])

            if not API_KEY:
                self._send(500, {"error": "Server is missing OPENAI_API_KEY."})
                return
            if not messages:
                self._send(400, {"error": "Missing messages."})
                return

            reply = do_chat(messages)
            self._send(200, {"reply": reply})

        except requests.HTTPError as e:
            detail = ""
            try:
                detail = e.response.json().get("error", {}).get("message", "")
            except Exception:
                pass
            self._send(e.response.status_code if e.response is not None else 500,
                       {"error": detail or "LLM API request failed."})
        except Exception as e:
            self._send(500, {"error": str(e)})

    def _send(self, status, obj):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
