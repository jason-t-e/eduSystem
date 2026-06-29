from fastapi import Request
from core.database.graph import KnowledgeGraph, LearnerGraph
from llm.client import LLMClient
from sqlalchemy.ext.asyncio import AsyncSession

# In a real app we'd inject these from app state or a DI container
def get_kg(request: Request) -> KnowledgeGraph:
    return request.app.state.kg

def get_lg(request: Request) -> LearnerGraph:
    return request.app.state.lg

def get_llm(request: Request) -> LLMClient:
    return request.app.state.llm

def get_db(request: Request) -> AsyncSession:
    # This would typically yield a session from async_sessionmaker
    return request.app.state.db_session()
