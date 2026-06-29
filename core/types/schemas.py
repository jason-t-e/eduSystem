from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass, field
from datetime import datetime

class Level(str, Enum):
    ANALOGY = "analogy"
    LAYMAN = "layman"
    STUDENT = "student"
    EXPERT = "expert"
    MATH = "math"

class SourceRef(BaseModel):
    file_name: str
    heading_path: str
    page: Optional[int] = None
    chunk_index: int

class Property(BaseModel):
    name: str
    value: str
    unit: Optional[str] = None
    confidence: float
    source: SourceRef

class Function(BaseModel):
    name: str
    formula: str
    description: str
    variables: Dict[str, str]
    confidence: float
    source: SourceRef

class Example(BaseModel):
    text: str
    difficulty: int
    steps: List[str]
    confidence: float
    source: SourceRef

class Misconception(BaseModel):
    description: str
    warning_signs: List[str]
    fixes: List[str]
    frequency: str
    confidence: float
    source: SourceRef

class PedagogyMeta(BaseModel):
    difficulty: int
    prerequisite_hints: List[str]
    teaching_notes: List[str]
    common_sticking_points: List[str]

class ExamMeta(BaseModel):
    weightage: str
    question_types: List[str]
    board_tags: List[str]
    chapter_ref: str

class ConceptObject(BaseModel):
    id: str
    name: str
    subject: str
    grade: int
    version: int = 1
    is_deprecated: bool = False
    confidence_score: float
    definition: str
    intuition: str
    aliases: List[str] = Field(default_factory=list)
    domain_tags: List[str] = Field(default_factory=list)
    properties: List[Property] = Field(default_factory=list)
    functions: List[Function] = Field(default_factory=list)
    explanations: Dict[Level, str] = Field(default_factory=dict)
    examples: List[Example] = Field(default_factory=list)
    misconceptions: List[Misconception] = Field(default_factory=list)
    pedagogy_metadata: Optional[PedagogyMeta] = None
    exam_metadata: Optional[ExamMeta] = None
    field_confidence: Dict[str, float] = Field(default_factory=dict)
    sources: List[SourceRef] = Field(default_factory=list)

class RelationType(str, Enum):
    REQUIRES = "REQUIRES"
    PART_OF = "PART_OF"
    RELATES_TO = "RELATES_TO"
    CONTRASTS_WITH = "CONTRASTS_WITH"
    TESTED_BY = "TESTED_BY"
    CONTRADICTS = "CONTRADICTS"

class TypedRelation(BaseModel):
    source_id: str
    target_id: str
    relation_type: RelationType
    reason: Optional[str] = None
    strength: Optional[float] = None
    container_type: Optional[str] = None
    role: Optional[str] = None
    how: Optional[str] = None
    why: Optional[str] = None
    confidence: float = 1.0

class ConceptState(str, Enum):
    UNKNOWN = "UNKNOWN"
    LEARNING = "LEARNING"
    REVIEWING = "REVIEWING"
    MASTERED = "MASTERED"

class LearnerConceptState(BaseModel):
    student_id: str
    concept_id: str
    state: ConceptState = ConceptState.UNKNOWN
    mastery: float = 0.0
    confidence: float = 0.0
    calibration_error: float = 0.0
    forgetting_score: float = 0.0
    next_review: Optional[datetime] = None
    explanation_level: Level = Level.STUDENT
    active_misconceptions: List[str] = Field(default_factory=list)

class FrictionState(str, Enum):
    SMOOTH = "SMOOTH"
    STRUGGLING = "STRUGGLING"
    STUCK = "STUCK"

class LearningStage(str, Enum):
    NOVICE = "NOVICE"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

class SelfAssessLevel(str, Enum):
    CONFIDENT = "CONFIDENT"
    WEAK = "WEAK"
    UNKNOWN = "UNKNOWN"

class StudentProfile(BaseModel):
    id: str
    name: str
    target_exam: Optional[str] = None
    exam_deadline: Optional[datetime] = None
    learning_stage: LearningStage = LearningStage.NOVICE

class SessionPlanItem(BaseModel):
    concept_id: str
    activity_type: str
    reasons: List[str] = Field(default_factory=list)
    estimated_minutes: int

class SessionPlan(BaseModel):
    id: str
    student_id: str
    items: List[SessionPlanItem] = Field(default_factory=list)
    total_estimated_minutes: int = 0

@dataclass
class SessionEvent:
    event_id: str
    session_id: str
    timestamp: datetime
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AttemptRecorded(SessionEvent):
    event_type: str = "AttemptRecorded"

@dataclass
class ConceptTaught(SessionEvent):
    event_type: str = "ConceptTaught"

@dataclass
class DiagnosticStarted(SessionEvent):
    event_type: str = "DiagnosticStarted"

@dataclass
class IngestionCompleted(SessionEvent):
    event_type: str = "IngestionCompleted"

@dataclass
class ImprovementProposed(SessionEvent):
    event_type: str = "ImprovementProposed"
