import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    # Since we don't have the real app state initialized (no lifespan execution in TestClient by default unless using 'with TestClient(app):'),
    # we use a context manager to run the lifespan events and setup app.state
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()

def test_get_concept_graph():
    with TestClient(app) as client:
        response = client.get("/api/v1/graph/c1")
        assert response.status_code == 200
        assert "elements" in response.json()

def test_get_learner_graph():
    with TestClient(app) as client:
        response = client.get("/api/v1/graph/c1/learner/s1")
        assert response.status_code == 200
        assert "elements" in response.json()
