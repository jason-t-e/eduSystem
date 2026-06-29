import pytest
from llm.prompt_registry import PromptRegistry

def test_prompt_registry():
    registry = PromptRegistry("llm/prompts")
    prompt = registry.render("concept_extraction", version=1, text="Test text", heading_path="H1", source_file="f.md", chunk_index=0)
    assert "Test text" in prompt
    assert "H1" in prompt
