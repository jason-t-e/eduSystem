import json
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field

from llm.client import LLMClient
from llm.validators import parse_with_retry
from agents.ingestion.chunker import Chunk
from agents.ingestion.ontology_mapper import OntologyMapper
from core.types.schemas import ConceptObject, TypedRelation, RelationType, SourceRef
from core.logging import get_logger

_log = get_logger(__name__)

class RawRelation(BaseModel):
    target_name: str
    relation_type: RelationType
    reason: str

class RawConcept(BaseModel):
    name: str
    definition: str
    intuition: str
    properties: List[Dict[str, Any]] = Field(default_factory=list)
    relations: List[RawRelation] = Field(default_factory=list)

class ExtractionResult(BaseModel):
    concepts: List[RawConcept]

class Extractor:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.jinja_env = Environment(loader=FileSystemLoader("llm/prompts"))
        self.mapper = OntologyMapper()

    async def process_chunk(self, chunk: Chunk) -> List[ConceptObject]:
        template = self.jinja_env.get_template("concept_extraction_v1.j2")
        prompt = template.render(
            text=chunk.text,
            heading_path=chunk.heading_path,
            source_file=chunk.source_file,
            chunk_index=chunk.chunk_index
        )

        response = await self.llm.complete(
            system="You are an expert educational ontologist extracting domain knowledge for high school students. Always return pure JSON.",
            user=prompt
        )

        # We parse it as a generic List to avoid complex dynamic Pydantic structures for the first pass
        try:
            from llm.validators import _strip_markdown_fences, _extract_json_from_text
            cleaned = _strip_markdown_fences(response)
            extracted = _extract_json_from_text(cleaned)
            data = json.loads(extracted)
            if not isinstance(data, list):
                if isinstance(data, dict) and "concepts" in data:
                    data = data["concepts"]
                else:
                    data = [data]
        except Exception as e:
            _log.error(f"Failed to parse extraction: {e}")
            return [], []

        concepts = []
        relations = []

        source = SourceRef(
            file_name=chunk.source_file,
            heading_path=chunk.heading_path,
            page=chunk.page_estimate,
            chunk_index=chunk.chunk_index
        )

        for item in data:
            raw_name = item.get("name", "Unknown Concept")
            canon_name = self.mapper.get_canonical_name(raw_name)
            cid = self.mapper.generate_id(canon_name)

            c = ConceptObject(
                id=cid,
                name=canon_name,
                subject="Accountancy",
                grade=11,
                confidence_score=0.8,
                definition=item.get("definition", ""),
                intuition=item.get("intuition", ""),
                sources=[source]
            )
            concepts.append(c)

            for rel in item.get("relations", []):
                target_raw = rel.get("target_name")
                if target_raw:
                    target_canon = self.mapper.get_canonical_name(target_raw)
                    target_id = self.mapper.generate_id(target_canon)

                    r = TypedRelation(
                        source_id=cid,
                        target_id=target_id,
                        relation_type=RelationType(rel.get("relation_type", "RELATES_TO")),
                        reason=rel.get("reason", "")
                    )
                    relations.append(r)

        return concepts, relations
