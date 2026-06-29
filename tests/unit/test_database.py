import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.database.models import Base, StudentModel
from core.database.graph import KnowledgeGraph, LearnerGraph
from core.types.schemas import ConceptObject, TypedRelation, RelationType, SourceRef

@pytest.fixture
async def sqlite_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session

@pytest.fixture
def kuzu_db(tmp_path):
    kg_path = str(tmp_path / "kg")
    lg_path = str(tmp_path / "lg")
    kg = KnowledgeGraph(kg_path)
    lg = LearnerGraph(lg_path)
    return kg, lg

@pytest.mark.asyncio
async def test_sqlite_student_insert(sqlite_session):
    student = StudentModel(id="s1", name="Test Student")
    sqlite_session.add(student)
    await sqlite_session.commit()

    result = await sqlite_session.get(StudentModel, "s1")
    assert result is not None
    assert result.name == "Test Student"

def test_kuzu_concept_upsert(kuzu_db):
    kg, _ = kuzu_db
    source = SourceRef(file_name="t", heading_path="H", chunk_index=0)
    c1 = ConceptObject(
        id="c1", name="Concept 1", subject="Math", grade=11, confidence_score=1.0,
        definition="D1", intuition="I1"
    )
    c2 = ConceptObject(
        id="c2", name="Concept 2", subject="Math", grade=11, confidence_score=1.0,
        definition="D2", intuition="I2"
    )
    kg.upsert_concept(c1)
    kg.upsert_concept(c2)

    # Check if they exist
    res = kg.conn.execute("MATCH (c:Concept) RETURN c.id;").get_as_df()
    assert len(res) == 2
    assert "c1" in res["c.id"].tolist()

    rel = TypedRelation(source_id="c1", target_id="c2", relation_type=RelationType.REQUIRES, reason="test")
    kg.insert_relation(rel)

    res_rel = kg.conn.execute("MATCH (a)-[r:REQUIRES]->(b) RETURN r.reason;").get_as_df()
    assert len(res_rel) == 1
    assert res_rel.iloc[0]["r.reason"] == "test"
