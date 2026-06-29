from typing import List, Tuple
from core.types.schemas import ConceptObject, TypedRelation
from core.logging import get_logger

_log = get_logger(__name__)

class Validator:
    def __init__(self, confidence_threshold: float = 0.6):
        self.threshold = confidence_threshold

    def validate(self, concepts: List[ConceptObject], relations: List[TypedRelation]) -> Tuple[List[ConceptObject], List[TypedRelation]]:
        valid_concepts = []
        valid_relations = []

        for c in concepts:
            if c.confidence_score >= self.threshold:
                valid_concepts.append(c)
            else:
                _log.warning(f"Concept {c.id} below confidence threshold: {c.confidence_score}")

        valid_c_ids = {c.id for c in valid_concepts}

        for r in relations:
            # We assume for now that relationships only link to valid concepts
            if r.confidence >= self.threshold and r.source_id in valid_c_ids:
                valid_relations.append(r)
            else:
                _log.warning(f"Relation from {r.source_id} to {r.target_id} dropped (low confidence or missing source)")

        return valid_concepts, valid_relations
