# tests/unit/test_llm_client.py
import pytest
from unittest.mock import AsyncMock, patch
from llm.client import OllamaClient, LLMClient
from llm.validators import parse_with_retry, _strip_markdown_fences
from pydantic import BaseModel


class SimpleSchema(BaseModel):
    answer: str
    confidence: float


# --- Protocol tests ---

def test_ollama_client_satisfies_protocol():
    """OllamaClient must satisfy the LLMClient Protocol."""
    client = OllamaClient()
    assert isinstance(client, LLMClient)


# --- Validator tests ---

def test_strip_markdown_fences_json():
    raw = '```json\n{"answer": "yes"}\n```'
    result = _strip_markdown_fences(raw)
    assert result == '{"answer": "yes"}'


def test_strip_markdown_fences_plain():
    raw = '```\n{"answer": "yes"}\n```'
    result = _strip_markdown_fences(raw)
    assert result == '{"answer": "yes"}'


def test_strip_no_fences_unchanged():
    raw = '{"answer": "yes"}'
    result = _strip_markdown_fences(raw)
    assert result == '{"answer": "yes"}'


@pytest.mark.asyncio
async def test_parse_with_retry_clean_json():
    raw = '{"answer": "double entry", "confidence": 0.9}'
    result = await parse_with_retry(raw, SimpleSchema)
    assert result.answer == "double entry"
    assert result.confidence == 0.9


@pytest.mark.asyncio
async def test_parse_with_retry_fenced_json():
    raw = '```json\n{"answer": "double entry", "confidence": 0.9}\n```'
    result = await parse_with_retry(raw, SimpleSchema)
    assert result.answer == "double entry"


@pytest.mark.asyncio
async def test_parse_with_retry_json_in_prose():
    raw = 'Here is the result: {"answer": "double entry", "confidence": 0.9} hope that helps!'
    result = await parse_with_retry(raw, SimpleSchema)
    assert result.answer == "double entry"


@pytest.mark.asyncio
async def test_parse_with_retry_raises_on_bad_json():
    raw = "this is not json at all"
    with pytest.raises(ValueError, match="Failed to parse"):
        await parse_with_retry(raw, SimpleSchema, llm_client=None)
