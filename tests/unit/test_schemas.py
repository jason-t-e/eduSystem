import pytest
from datetime import datetime
from core.types.schemas import (
    ConceptObject, SourceRef, Level, RelationType, TypedRelation,
    StudentProfile, LearningStage, SessionEvent, IngestionCompleted
)

def test_concept_object_creation():
    source = SourceRef(file_name="test.pdf", heading_path="H1", chunk_index=0)
    concept = ConceptObject(
        id="acc11_ch1_concept1",
        name="Accounting",
        subject="Accountancy",
        grade=11,
        confidence_score=0.9,
        definition="The process of recording financial transactions.",
        intuition="Keeping track of money.",
        sources=[source]
    )
    assert concept.id == "acc11_ch1_concept1"
    assert concept.version == 1
    assert concept.is_deprecated is False

def test_typed_relation():
    relation = TypedRelation(
        source_id="c1",
        target_id="c2",
        relation_type=RelationType.REQUIRES,
        reason="C2 is needed to understand C1"
    )
    assert relation.relation_type == RelationType.REQUIRES
    assert relation.reason == "C2 is needed to understand C1"

def test_student_profile():
    student = StudentProfile(id="s1", name="John Doe")
    assert student.learning_stage == LearningStage.NOVICE

def test_events():
    event = IngestionCompleted(
        event_id="e1",
        session_id="s1",
        timestamp=datetime.now(),
        payload={"docs_processed": 5}
    )
    assert event.event_type == "IngestionCompleted"
    assert event.payload["docs_processed"] == 5
