# llm/client.py
import asyncio
import json
from typing import Protocol, AsyncIterator, runtime_checkable

import httpx
from loguru import logger

from config.settings import settings
from core.logging import get_logger


@runtime_checkable
class LLMClient(Protocol):
    """
    Interface for all LLM clients. Every agent receives an LLMClient via
    dependency injection. Never import OllamaClient directly in agents.

    To add a new LLM provider:
    1. Create a new class implementing complete() and stream()
    2. Change get_llm() in api/deps.py
    3. Zero changes anywhere else
    """

    async def complete(self, system: str, user: str) -> str:
        """Single-shot completion. Returns the full response as a string."""
        ...

    async def stream(self, system: str, user: str) -> AsyncIterator[str]:
        """Streaming completion. Yields text chunks as they arrive."""
        ...

    async def health_check(self) -> bool:
        """Returns True if the LLM service is reachable and the model is available."""
        ...


class OllamaClient:
    """
    Concrete implementation of LLMClient for Ollama.
    Uses httpx async for all HTTP calls.
    Implements exponential backoff retry on failure.
    """

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: float = None,
        max_retries: int = None,
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.llm_timeout_seconds
        self.max_retries = max_retries or settings.llm_max_retries
        self._log = get_logger(__name__)

    async def complete(self, system: str, user: str) -> str:
        """
        Send a prompt and wait for the full response.
        Retries up to max_retries times with exponential backoff.
        Raises RuntimeError if all retries fail.
        """
        last_error = None

        for attempt in range(self.max_retries):
            if attempt > 0:
                wait_seconds = 2 ** attempt
                self._log.warning(
                    f"LLM retry {attempt}/{self.max_retries - 1} "
                    f"(waiting {wait_seconds}s): {last_error}"
                )
                await asyncio.sleep(wait_seconds)

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/api/chat",
                        json={
                            "model": self.model,
                            "messages": [
                                {"role": "system", "content": system},
                                {"role": "user", "content": user},
                            ],
                            "stream": False,
                        },
                    )
                    response.raise_for_status()
                    content = response.json()["message"]["content"]
                    self._log.debug(
                        f"LLM complete: {len(content)} chars "
                        f"(attempt {attempt + 1})"
                    )
                    return content

            except httpx.TimeoutException as e:
                last_error = f"Timeout after {self.timeout}s"
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            except Exception as e:
                last_error = str(e)

        raise RuntimeError(
            f"LLM complete failed after {self.max_retries} attempts. "
            f"Last error: {last_error}"
        )

    async def stream(self, system: str, user: str) -> AsyncIterator[str]:
        """
        Stream the response token by token.
        Yields each text chunk as it arrives from Ollama.
        Use for: teaching explanations, long-form content (better UX).
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("done"):
                            break
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        self._log.warning(f"Unparseable stream line: {line[:100]}")
                        continue

    async def health_check(self) -> bool:
        """Ping Ollama and confirm the model is loaded."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                models = [m["name"] for m in resp.json().get("models", [])]
                return self.model in models
        except Exception:
            return False