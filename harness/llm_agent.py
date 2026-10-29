"""A minimal real agent: Anthropic Messages API tool-use loop with one bash tool.

NOT TESTED against the real API (no key was available when this was written).
It is tested only with a fake client in test_harness.py. Expect to fix small API details on the first real run.

The key is read from the ANTHROPIC_API_KEY environment variable by the SDK. Never paste a key into a file.
SAFETY: the bash tool runs on whatever machine runs this. Run it inside Docker or a throwaway VM.
"""
SYSTEM = (
    "You are a coding agent working in a small Python repository with source code in src/ and tests in tests/. "
    "Use the bash tool to inspect files, edit code, and run tests (run `pytest -q` from the repository root). "
    "Edit files with shell commands such as a heredoc or sed. "
    "When you are done, reply with a short final message and no tool call."
)

TOOLS = [{
    "name": "bash",
    "description": "Run a shell command in the repository root. Returns stdout and stderr.",
    "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
}]


def _make_client():
    import anthropic  # imported lazily so the rest of the harness works without it
    return anthropic.Anthropic()


class LLMAgent:
    def __init__(self, model="claude-haiku-5-5", max_steps=25, client=None):
        self.model, self.max_steps, self.client = model, max_steps, client
        self.usage = {"input_tokens": 0, "output_tokens": 0}

    def run(self, prompt, tool):
        client = self.client or _make_client()
        messages = [{"role": "user", "content": prompt}]
        for _ in range(self.max_steps):
            resp = client.messages.create(model=self.model, max_tokens=2048, system=SYSTEM,
                                          tools=TOOLS, messages=messages)
            u = getattr(resp, "usage", None)
            if u:
                self.usage["input_tokens"] += getattr(u, "input_tokens", 0)
                self.usage["output_tokens"] += getattr(u, "output_tokens", 0)
            messages.append({"role": "assistant", "content": resp.content})
            uses = [b for b in resp.content if b.type == "tool_use"]
            if not uses:
                return "".join(b.text for b in resp.content if b.type == "text")
            results = [{"type": "tool_result", "tool_use_id": b.id,
                        "content": tool.run(b.input.get("command", ""))} for b in uses]
            messages.append({"role": "user", "content": results})
        return "[stopped: max steps reached]"
