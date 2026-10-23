"""LLM explanations of the 2-3 biggest mistakes.

Providers are pluggable. Tests and CI always use MockProvider, so nobody needs an API key
to run them. Set GEMINI_API_KEY (see .env.example) to use Gemini for real.
"""

from __future__ import annotations

import os
from typing import Protocol

from dnb.coach.review import MoveReview


class LLMProvider(Protocol):
    def complete(self, prompt: str) -> str: ...


class MockProvider:
    def complete(self, prompt: str) -> str:
        return "This move left a box with three sides, so your opponent got a free box."


class GeminiProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        from google import genai  # optional dependency: `uv sync --extra llm`

        self.client = genai.Client(api_key=api_key or os.environ["GEMINI_API_KEY"])
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    def complete(self, prompt: str) -> str:
        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text or ""


def default_provider() -> LLMProvider:
    return GeminiProvider() if os.environ.get("GEMINI_API_KEY") else MockProvider()


def build_prompt(mistake: MoveReview) -> str:
    # TODO(P4): include only verified facts from the review (boxes given away, the better move)
    # so the explanation can't invent things that didn't happen.
    raise NotImplementedError


def explain_mistakes(reviews: list[MoveReview], provider: LLMProvider | None = None) -> list[str]:
    # TODO(P4): pick the 2-3 biggest mistakes, build prompts, call provider.complete().
    raise NotImplementedError
