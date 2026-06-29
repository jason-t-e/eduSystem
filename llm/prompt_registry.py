from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from core.logging import get_logger

_log = get_logger(__name__)

class PromptRegistry:
    def __init__(self, prompt_dir: str = "llm/prompts"):
        self.env = Environment(loader=FileSystemLoader(prompt_dir))

    def render(self, name: str, version: int = 1, **ctx) -> str:
        # Tries to find the specific version, otherwise falls back
        file_name = f"{name}_v{version}.j2"
        try:
            template = self.env.get_template(file_name)
            _log.debug(f"Rendered prompt {file_name}")
            return template.render(**ctx)
        except Exception as e:
            _log.error(f"Failed to load prompt {file_name}: {e}")
            raise
