"""Agent backed by a LOCAL model through Ollama's /api/chat. No API key, no network beyond localhost.

Start the server first:  ollama serve   (or open the Ollama app)
Use with the sandbox:    python3 run.py --agent ollama --sandbox
The model must support tool calling (llama3.2, qwen2.5-coder, qwen3 do; gemma3:1b does not).
"""
import json
import os
import urllib.error
import urllib.request

SYSTEM = (
    "You are a coding agent working in a small Python repository with source code in src/ and tests in tests/. "
    "Use the bash tool to inspect files, edit code, and run tests (run `pytest -q` from the repository root). "
    "Edit files with shell commands such as a heredoc or sed. "
    "When you are done, reply with a short final message and no tool call."
)

TOOLS = [{
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run a shell command in the repository root. Returns stdout and stderr.",
        "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
    },
}]


def text_tool_call(content):
    """Small models often write the tool call as JSON text instead of a real tool call. Return the command or None."""
    i = (content or "").find('{"name"')
    if i < 0:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(content[i:])
    except ValueError:
        return None
    args = obj.get("parameters") or obj.get("arguments") or {}
    if obj.get("name") == "bash" and isinstance(args, dict) and isinstance(args.get("command"), str):
        return args["command"]
    return None


def _http_post(url, payload, timeout=900):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


class OllamaAgent:
    def __init__(self, model="llama3.2:latest", host=None, max_steps=15,
                 temperature=0.7, num_ctx=8192, post=None, think=None):
        host = host or os.environ.get("OLLAMA_HOST") or "127.0.0.1:11434"   # OLLAMA_HOST may be host:port without a scheme
        self.model, self.host, self.max_steps = model, (host if "://" in host else "http://" + host), max_steps
        self.temperature, self.num_ctx = temperature, num_ctx
        self.post = post or _http_post
        self.think = think   # False turns off Qwen3-style reasoning text; None leaves the model default
        self.usage = {"input_tokens": 0, "output_tokens": 0}
        self.text_tool_calls = 0
        self.malformed_calls = 0

    def run(self, prompt, tool):
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]
        bad_in_a_row = 0
        for _ in range(self.max_steps):
            body = {
                "model": self.model, "messages": messages, "tools": TOOLS, "stream": False,
                "options": {"temperature": self.temperature, "seed": getattr(tool, "seed", 0), "num_ctx": self.num_ctx},
            }
            if self.think is not None:
                body["think"] = self.think
            try:
                resp = self.post(self.host + "/api/chat", body)
                bad_in_a_row = 0
            except urllib.error.HTTPError as e:
                if e.code != 500:
                    raise
                # Ollama answers 500 when the model's tool call cannot be parsed. That is the agent's output, not a server
                # fault: count it, tell the model, and let it try again. Three in a row ends the episode.
                self.malformed_calls += 1
                bad_in_a_row += 1
                if bad_in_a_row >= 3:
                    return "[stopped: malformed tool calls]"
                messages.append({"role": "user", "content": "Your last tool call could not be parsed. Call the bash tool "
                                                             "again with a valid command."})
                continue
            self.usage["input_tokens"] += resp.get("prompt_eval_count", 0)
            self.usage["output_tokens"] += resp.get("eval_count", 0)
            msg = resp["message"]
            messages.append(msg)
            calls = msg.get("tool_calls") or []
            if not calls:
                cmd = text_tool_call(msg.get("content", ""))
                if cmd is None:
                    return msg.get("content", "")
                self.text_tool_calls += 1
                messages.append({"role": "tool", "tool_name": "bash", "content": tool.run(cmd)})
                continue
            for c in calls:
                fn = c.get("function", {})
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except ValueError:
                        args = {}
                out = tool.run(args.get("command", "")) if fn.get("name") == "bash" else f"unknown tool {fn.get('name')}"
                messages.append({"role": "tool", "tool_name": fn.get("name", "bash"), "content": out})
        return "[stopped: max steps reached]"
