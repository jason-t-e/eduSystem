import asyncio
import os
from pathlib import Path
from agents.ingestion.chunker import chunk_markdown
from agents.ingestion.extractor import Extractor
from agents.ingestion.validator import Validator
from core.database.graph import KnowledgeGraph
from config.settings import settings
from core.logging import get_logger

# Placeholder imports
# from llm.ollama_client import OllamaClient

_log = get_logger(__name__)

async def run_ingestion(source_dir: str, kg: KnowledgeGraph, llm_client):
    """
    Reads markdown files from source_dir, chunks them, extracts concepts,
    validates them, and upserts into Knowledge Graph.
    """
    extractor = Extractor(llm_client)
    validator = Validator()

    docs = list(Path(source_dir).glob("*.md"))
    if not docs:
        _log.warning(f"No markdown documents found in {source_dir}")
        return

    for doc in docs:
        _log.info(f"Processing {doc.name}")
        with open(doc, 'r') as f:
            content = f.read()

        chunks = chunk_markdown(content, doc.name)

        all_concepts = []
        all_relations = []

        for chunk in chunks:
            concepts, relations = await extractor.process_chunk(chunk)
            all_concepts.extend(concepts)
            all_relations.extend(relations)

        valid_concepts, valid_relations = validator.validate(all_concepts, all_relations)

        for c in valid_concepts:
            kg.upsert_concept(c)

        for r in valid_relations:
            kg.insert_relation(r)

        _log.info(f"Ingested {len(valid_concepts)} concepts and {len(valid_relations)} relations from {doc.name}")

if __name__ == "__main__":
    pass
    # kg = KnowledgeGraph(settings.knowledge_graph_path)
    # llm = OllamaClient()
    # asyncio.run(run_ingestion(settings.markdown_cache_dir, kg, llm))
