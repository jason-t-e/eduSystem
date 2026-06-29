from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import json

from config.settings import settings
from core.database.graph import KnowledgeGraph, LearnerGraph
from llm.client import OllamaClient
from api.deps import get_kg, get_lg

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    settings.ensure_directories()
    app.state.kg = KnowledgeGraph(settings.knowledge_graph_path)
    app.state.lg = LearnerGraph(settings.learner_graph_path)
    app.state.llm = OllamaClient()
    yield
    # Teardown

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

@app.get("/health")
async def health_check(kg: KnowledgeGraph = Depends(get_kg)):
    try:
        # Check Kuzu
        res = kg.conn.execute("MATCH (c:Concept) RETURN count(c) as count;").get_as_df()
        concept_count = int(res.iloc[0]["count"])
    except Exception as e:
        concept_count = -1

    return {
        "status": "ok",
        "concept_count": concept_count,
        "kuzu_status": "ok" if concept_count >= 0 else "error"
    }

@app.get("/api/v1/graph/{concept_id}")
async def get_concept_graph(concept_id: str, kg: KnowledgeGraph = Depends(get_kg)):
    """Returns subgraph as Cytoscape.js JSON."""

    # Simple query: find the concept and its immediate neighbors
    query = """
    MATCH (a:Concept {id: $cid})-[r]->(b:Concept)
    RETURN a, r, b
    """
    try:
        res = kg.conn.execute(query, parameters={"cid": concept_id}).get_as_df()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    elements = []
    nodes_seen = set()

    for _, row in res.iterrows():
        # Kuzu returns node objects, we need to extract their properties
        # For simplicity in this mock response, we construct node payloads

        a_node = row['a']
        b_node = row['b']
        r_edge = row['r']

        a_id = a_node.get('_id', {}).get('offset') if isinstance(a_node, dict) else str(a_node)
        b_id = b_node.get('_id', {}).get('offset') if isinstance(b_node, dict) else str(b_node)

        # In a real implementation we would properly parse the Kuzu Node/Rel objects
        # Here we mock the Cytoscape structure based on the query result

        if a_id not in nodes_seen:
            elements.append({
                "data": {"id": f"node_{a_id}", "label": "Source Concept"}
            })
            nodes_seen.add(a_id)

        if b_id not in nodes_seen:
            elements.append({
                "data": {"id": f"node_{b_id}", "label": "Target Concept"}
            })
            nodes_seen.add(b_id)

        elements.append({
            "data": {
                "id": f"edge_{a_id}_{b_id}",
                "source": f"node_{a_id}",
                "target": f"node_{b_id}",
                "label": "RELATES_TO"
            }
        })

    if not elements:
        # Check if the concept exists at all but has no edges
        res_single = kg.conn.execute("MATCH (c:Concept {id: $cid}) RETURN c;", parameters={"cid": concept_id}).get_as_df()
        if not res_single.empty:
            elements.append({"data": {"id": concept_id, "label": concept_id}})

    return {"elements": elements}

@app.get("/api/v1/graph/{concept_id}/learner/{student_id}")
async def get_learner_graph(concept_id: str, student_id: str, kg: KnowledgeGraph = Depends(get_kg), lg: LearnerGraph = Depends(get_lg)):
    """Same as graph, but enriched with LearnerConceptState."""
    base_graph = await get_concept_graph(concept_id, kg)

    # Mock enrichment
    for elem in base_graph["elements"]:
        if "source" not in elem["data"]: # It's a node
            elem["data"]["mastery"] = 0.5
            elem["data"]["color"] = "#ffcc00" # yellow for medium mastery

    return base_graph
