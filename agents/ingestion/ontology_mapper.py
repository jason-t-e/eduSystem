import json
import re
from pathlib import Path
from config.settings import settings

class OntologyMapper:
    def __init__(self):
        # We assume the canonical names JSON is loaded from config
        self.mappings = {}
        self._load_mappings()

    def _load_mappings(self):
        path = Path("./config/ontology/commerce_11/canonical_names.json")
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
                self.mappings = data.get("mappings", {})

    def _normalize(self, name: str) -> str:
        return re.sub(r'[^a-z0-9]', '', name.lower())

    def get_canonical_name(self, raw_name: str) -> str:
        norm = raw_name.lower().strip()
        if norm in self.mappings:
            return self.mappings[norm]
        return raw_name.title()

    def generate_id(self, canonical_name: str, subject: str = "accountancy", grade: int = 11) -> str:
        slug = re.sub(r'[^a-z0-9]', '_', canonical_name.lower())
        return f"com{grade}_{subject[:3]}_{slug}_v1"
