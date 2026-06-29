import asyncio
import json
from llm.client import LLMClient
from llm.prompt_registry import PromptRegistry
from core.database.graph import KnowledgeGraph
from config.settings import settings
from core.logging import get_logger

# Placeholder import for actual Ollama client initialization in a real setup
# from llm.ollama_client import OllamaClient

_log = get_logger(__name__)

async def precompute(kg: KnowledgeGraph, llm: LLMClient):
    """Loops through concepts and precomputes missing explanations."""
    registry = PromptRegistry()

    # Fetch concepts
    res = kg.conn.execute("MATCH (c:Concept) RETURN c.id, c.name, c.definition, c.intuition, c.explanations;").get_as_df()

    for _, row in res.iterrows():
        cid = row['c.id']
        explanations_str = row['c.explanations']

        try:
            explanations = json.loads(explanations_str)
        except:
            explanations = {}

        # Check if we have all 5 levels
        levels = ["analogy", "layman", "student", "expert", "math"]
        missing = [lvl for lvl in levels if lvl not in explanations]

        if missing:
            _log.info(f"Precomputing explanations for {cid}")
            prompt = registry.render(
                "precompute_explanations",
                version=1,
                name=row['c.name'],
                definition=row['c.definition'],
                intuition=row['c.intuition']
            )

            response = await llm.complete(
                system="You are an expert educator. Output pure JSON.",
                user=prompt
            )

            try:
                from llm.validators import _strip_markdown_fences
                cleaned = _strip_markdown_fences(response)
                new_expls = json.loads(cleaned)
                explanations.update(new_expls)

                # Update in Kuzu
                new_expls_str = json.dumps(explanations)
                kg.conn.execute(
                    "MATCH (c:Concept {id: $id}) SET c.explanations = $expls",
                    parameters={"id": cid, "expls": new_expls_str}
                )
            except Exception as e:
                _log.error(f"Failed to generate explanations for {cid}: {e}")

if __name__ == "__main__":
    pass
    # kg = KnowledgeGraph(settings.knowledge_graph_path)
    # llm = OllamaClient()
    # asyncio.run(precompute(kg, llm))
