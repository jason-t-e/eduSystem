# llm/validators.py
import json
import re
from typing import TypeVar, Type

from pydantic import BaseModel, ValidationError

from core.logging import get_logger

T = TypeVar("T", bound=BaseModel)

_log = get_logger(__name__)


def _strip_markdown_fences(text: str) -> str:
    """
    Strip ```json ... ``` or ``` ... ``` wrappers that LLMs often add.
    Also handles single-line JSON that has leading/trailing whitespace.
    """
    # Pattern: optional ```json or ``` at start, optional ``` at end
    pattern = r"^```(?:json)?\s*\n?(.*?)\n?```$"
    match = re.match(pattern, text.strip(), re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def _extract_json_from_text(text: str) -> str:
    """
    Last resort: find the first { or [ and extract to matching } or ].
    Handles cases where the LLM adds explanation before/after the JSON.
    """
    # Try to find JSON object
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        if start == -1:
            continue
        # Find the matching close by tracking nesting
        depth = 0
        for i, char in enumerate(text[start:], start):
            if char == start_char:
                depth += 1
            elif char == end_char:
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return text


async def parse_with_retry(
    raw: str,
    schema: Type[T],
    llm_client=None,
    retries: int = 2,
) -> T:
    """
    Parse LLM output into a Pydantic schema.

    Attempt order:
    1. Direct JSON parse after stripping markdown fences
    2. Extract JSON from surrounding text
    3. (If llm_client provided) Ask LLM to fix the JSON, try again

    Args:
        raw: Raw text from LLM
        schema: Pydantic model class to parse into
        llm_client: Optional LLMClient to use for correction prompt
        retries: Number of correction attempts

    Returns:
        Parsed schema instance

    Raises:
        ValueError: If parsing fails after all retries
    """
    last_error = None

    # Attempt 1: Strip fences and parse
    cleaned = _strip_markdown_fences(raw)
    try:
        data = json.loads(cleaned)
        return schema.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        last_error = str(e)
        _log.debug(f"Direct parse failed: {e}")

    # Attempt 2: Extract JSON from surrounding text
    extracted = _extract_json_from_text(cleaned)
    try:
        data = json.loads(extracted)
        return schema.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as e:
        last_error = str(e)
        _log.debug(f"Extraction parse failed: {e}")

    # Attempt 3+: Ask LLM to fix it (only if client provided)
    if llm_client is None:
        raise ValueError(
            f"Failed to parse LLM output into {schema.__name__}. "
            f"Last error: {last_error}. Raw output: {raw[:300]}"
        )

    schema_example = schema.model_json_schema()

    for attempt in range(retries):
        _log.warning(f"Asking LLM to fix JSON (attempt {attempt + 1}/{retries})")
        correction_prompt = (
            f"The following text should be valid JSON matching this schema:\n"
            f"{json.dumps(schema_example, indent=2)}\n\n"
            f"Here is the broken output:\n{raw}\n\n"
            f"Return ONLY valid JSON. No explanation. No markdown fences."
        )
        try:
            fixed = await llm_client.complete(
                system="You are a JSON repair tool. Return only valid JSON.",
                user=correction_prompt,
            )
            cleaned_fixed = _strip_markdown_fences(fixed)
            data = json.loads(cleaned_fixed)
            return schema.model_validate(data)
        except Exception as e:
            last_error = str(e)
            _log.warning(f"LLM correction attempt {attempt + 1} failed: {e}")

    raise ValueError(
        f"Failed to parse LLM output into {schema.__name__} after {retries} "
        f"correction attempts. Last error: {last_error}"
    )