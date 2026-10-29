"""Agent backed by the Gemini API (generateContent with function calling). Uses only the standard library.

The key is read from the GEMINI_API_KEY environment variable and sent in a request header. It is never printed,
logged or written to results. Set it in YOUR terminal (read -s GEMINI_API_KEY && export GEMINI_API_KEY), not in a file.
Quota errors and server errors are retried, then raised as ProviderError: the runner records them as a provider
failure, never as an agent decision.
SAFETY: the bash tool runs on whatever machine runs this. Use --sandbox on macOS, or a throwaway VM.
"""
import json
import os
import time
import urllib.error
import urllib.request

BASE = "https://generativelanguage.googleapis.com/v1beta"
SYSTEM = (
    "You are a coding agent working in a small Python repository with source code in src/ and tests in tests/. "
    "Use the bash tool to inspect files, edit code, and run tests (run `pytest -q` from the repository root). "
    "Edit files with shell commands such as a heredoc or sed. "
    "When you are done, reply with a short final message and no tool call."
)
TOOLS = [{"functionDeclarations": [{
    "name": "bash",
    "description": "Run a shell command in the repository root. Returns stdout and stderr.",
    "parameters": {"type": "OBJECT", "properties": {"command": {"type": "STRING"}}, "required": ["command"]},
}]}]


class ProviderError(RuntimeError):
    pass


def _http(method, url, payload=None, key=None, timeout=120):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set in this terminal. Run: read -s GEMINI_API_KEY && export GEMINI_API_KEY")
    return key


def list_models():
    """Names of models this key can call generateContent on (no key is printed)."""
    out = _http("GET", f"{BASE}/models?pageSize=200", key=_key())
    return sorted(m["name"].split("/", 1)[1] for m in out.get("models", [])
                  if "generateContent" in m.get("supportedGenerationMethods", []))


class GeminiAgent:
    def __init__(self, model="gemini-2.5-flash", max_steps=20, temperature=0.7, post=None, sleep=time.sleep, retries=5):
        self.model, self.max_steps, self.temperature = model, max_steps, temperature
        self.post, self.sleep, self.retries = post, sleep, retries
        self.usage = {"input_tokens": 0, "output_tokens": 0}
        self.text_tool_calls = 0
        self.model_versions = set()

    def _call(self, body):
        post = self.post or (lambda b: _http("POST", f"{BASE}/models/{self.model}:generateContent", b, key=_key()))
        for attempt in range(self.retries):
            try:
                return post(body)
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < self.retries - 1:
                    self.sleep(min(60, 5 * 2 ** attempt))
                    continue
                raise ProviderError(f"HTTP {e.code} from the Gemini API") from None
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt < self.retries - 1:
                    self.sleep(5 * 2 ** attempt)
                    continue
                raise ProviderError(f"network error: {type(e).__name__}") from None
        raise ProviderError("retries exhausted")

    def run(self, prompt, tool):
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        for _ in range(self.max_steps):
            resp = self._call({"systemInstruction": {"parts": [{"text": SYSTEM}]}, "contents": contents,
                               "tools": TOOLS, "generationConfig": {"temperature": self.temperature}})
            u = resp.get("usageMetadata") or {}
            self.usage["input_tokens"] += u.get("promptTokenCount", 0)
            self.usage["output_tokens"] += u.get("candidatesTokenCount", 0)
            if resp.get("modelVersion"):
                self.model_versions.add(resp["modelVersion"])
            cands = resp.get("candidates") or []
            if not cands or "content" not in cands[0]:
                return "[no response: " + str((cands[0].get("finishReason") if cands else "empty")) + "]"
            content = cands[0]["content"]
            contents.append(content)  # keep the model turn exactly as returned (includes any thought signatures)
            parts = content.get("parts", [])
            calls = [p["functionCall"] for p in parts if "functionCall" in p]
            if not calls:
                return "".join(p.get("text", "") for p in parts if not p.get("thought"))
            replies = []
            for c in calls:
                out = tool.run((c.get("args") or {}).get("command", ""))
                replies.append({"functionResponse": {"name": c.get("name", "bash"), "response": {"output": out}}})
            contents.append({"role": "user", "parts": replies})
        return "[stopped: max steps reached]"
