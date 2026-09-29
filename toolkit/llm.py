"""Thin, testable wrapper around an LLM.

The backend is just a callable: (system, prompt, temperature, max_tokens) -> str.
By default it uses the Anthropic API; tests inject a fake backend, so no key is needed.
"""
import json
import os
import re
from typing import Callable, Optional

Backend = Callable[[str, str, float, int], str]

DEFAULT_MODEL = os.getenv("TOOLKIT_MODEL", "claude-sonnet-5-5")


def _anthropic_backend(model: str) -> Backend:
    import anthropic  # imported lazily so tests run without an API key

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    def call(system: str, prompt: str, temperature: float, max_tokens: int) -> str:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

    return call


class LLM:
    def __init__(self, backend: Optional[Backend] = None, model: str = DEFAULT_MODEL):
        self.model = model
        self._backend = backend or _anthropic_backend(model)
        self.calls = 0

    def complete(self, prompt: str, system: str = "", temperature: float = 0.2,
                 max_tokens: int = 800) -> str:
        self.calls += 1
        return self._backend(system, prompt, temperature, max_tokens).strip()

    def complete_json(self, prompt: str, system: str = "", retries: int = 1, **kw):
        """Ask for JSON; if parsing fails, ask the model to repair its own output."""
        text = self.complete(prompt, system, **kw)
        for attempt in range(retries + 1):
            try:
                return extract_json(text)
            except ValueError as err:
                if attempt == retries:
                    raise
                text = self.complete(
                    f"Your previous reply was not valid JSON ({err}).\n"
                    f"Return ONLY the corrected JSON, nothing else.\n\nPrevious reply:\n{text}",
                    system, **kw)


def extract_json(text: str):
    """Parse JSON from a model reply, tolerating ```json fences and surrounding prose."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for open_c, close_c in (("{", "}"), ("[", "]")):
        start, end = text.find(open_c), text.rfind(close_c)
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("no valid JSON found")
