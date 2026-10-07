"""
AI provider abstraction. Per project decision, no AI provider is wired up
yet (ANTHROPIC_API_KEY / AI_PROVIDER are unset). This module defines the
interface every AI feature calls, and a NotConfiguredProvider that raises a
clear, actionable error — so routes/services can be built and tested now,
and swapping in a real provider later is a one-file change here plus
setting the env vars, not a rewrite of the AI feature routes.
"""
from abc import ABC, abstractmethod
from functools import lru_cache

from app.core.config import settings


class AIProviderNotConfiguredError(Exception):
    pass


class AIProvider(ABC):
    @abstractmethod
    def summarize(self, text: str) -> str: ...

    @abstractmethod
    def answer_question(self, text: str, question: str) -> str: ...

    @abstractmethod
    def translate(self, text: str, target_language: str) -> str: ...

    @abstractmethod
    def extract_keywords(self, text: str) -> list[str]: ...

    @abstractmethod
    def suggest_title(self, text: str) -> str: ...


class NotConfiguredProvider(AIProvider):
    def _raise(self):
        raise AIProviderNotConfiguredError(
            "No AI provider is configured. Set AI_PROVIDER and the matching "
            "API key (e.g. ANTHROPIC_API_KEY) in .env, then implement the "
            "corresponding provider class in app/services/ai/."
        )

    def summarize(self, text: str) -> str:
        self._raise()

    def answer_question(self, text: str, question: str) -> str:
        self._raise()

    def translate(self, text: str, target_language: str) -> str:
        self._raise()

    def extract_keywords(self, text: str) -> list[str]:
        self._raise()

    def suggest_title(self, text: str) -> str:
        self._raise()


@lru_cache
def get_ai_provider() -> AIProvider:
    if settings.AI_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        # Implemented once the provider decision is made — see
        # docs/01-requirements.md "Out of scope for this phase".
        raise NotImplementedError("AnthropicProvider is not implemented yet.")
    return NotConfiguredProvider()
