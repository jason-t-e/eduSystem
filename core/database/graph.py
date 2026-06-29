import json
import kuzu
from typing import List, Dict, Optional, Any
from pathlib import Path

from core.logging import get_logger
from core.types.schemas import ConceptObject, TypedRelation

_log = get_logger(__name__)

class KnowledgeGraph:
    """Wrapper around Kuzu for the Knowledge Graph (Concepts and Typed Relations)."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = kuzu.Database(self.db_path)
        self.conn = kuzu.Connection(self.db)
        self._init_schema()

    def _init_schema(self):
        """Initialize the Knowledge Graph schema if it doesn't exist."""
        # Check existing tables
        tables = self.conn.execute("CALL show_tables() RETURN *;").get_as_df()
        table_names = tables['name'].tolist() if not tables.empty else []

        # Create Concept Node Table
        if "Concept" not in table_names:
            _log.info("Creating Concept node table in Kuzu")
            self.conn.execute("""
            CREATE NODE TABLE Concept (
                id STRING,
                name STRING,
                subject STRING,
                grade INT64,
                version INT64,
                is_deprecated BOOLEAN,
                confidence_score DOUBLE,
                definition STRING,
                intuition STRING,
                aliases STRING,
                domain_tags STRING,
                properties STRING,
                functions STRING,
                explanations STRING,
                examples STRING,
                misconceptions STRING,
                pedagogy_metadata STRING,
                exam_metadata STRING,
                field_confidence STRING,
                sources STRING,
                PRIMARY KEY (id)
            );
            """)

        # Define edge tables
        edge_tables = {
            "REQUIRES": "reason STRING, strength DOUBLE, confidence DOUBLE",
            "PART_OF": "container_type STRING, role STRING, how STRING, why STRING, confidence DOUBLE",
            "RELATES_TO": "reason STRING, confidence DOUBLE",
            "CONTRASTS_WITH": "reason STRING, confidence DOUBLE",
            "TESTED_BY": "reason STRING, confidence DOUBLE",
            "CONTRADICTS": "reason STRING, confidence DOUBLE",
        }

        for edge_name, props in edge_tables.items():
            if edge_name not in table_names:
                _log.info(f"Creating {edge_name} edge table in Kuzu")
                self.conn.execute(f"""
                CREATE REL TABLE {edge_name} (
                    FROM Concept TO Concept,
                    {props}
                );
                """)

    def upsert_concept(self, concept: ConceptObject):
        """Insert or update a ConceptObject."""
        # Convert nested objects to JSON strings
        props = concept.model_dump()
        for key in ["aliases", "domain_tags", "properties", "functions", "explanations", "examples",
                    "misconceptions", "field_confidence", "sources"]:
            props[key] = json.dumps(props[key])

        props["pedagogy_metadata"] = json.dumps(props["pedagogy_metadata"]) if props["pedagogy_metadata"] else "{}"
        props["exam_metadata"] = json.dumps(props["exam_metadata"]) if props["exam_metadata"] else "{}"

        query = """
        MERGE (c:Concept {id: $id})
        ON CREATE SET c.name = $name, c.subject = $subject, c.grade = $grade, c.version = $version,
                      c.is_deprecated = $is_deprecated, c.confidence_score = $confidence_score,
                      c.definition = $definition, c.intuition = $intuition, c.aliases = $aliases,
                      c.domain_tags = $domain_tags, c.properties = $properties, c.functions = $functions,
                      c.explanations = $explanations, c.examples = $examples, c.misconceptions = $misconceptions,
                      c.pedagogy_metadata = $pedagogy_metadata, c.exam_metadata = $exam_metadata,
                      c.field_confidence = $field_confidence, c.sources = $sources
        ON MATCH SET c.name = $name, c.subject = $subject, c.grade = $grade, c.version = $version,
                     c.is_deprecated = $is_deprecated, c.confidence_score = $confidence_score,
                     c.definition = $definition, c.intuition = $intuition, c.aliases = $aliases,
                     c.domain_tags = $domain_tags, c.properties = $properties, c.functions = $functions,
                     c.explanations = $explanations, c.examples = $examples, c.misconceptions = $misconceptions,
                     c.pedagogy_metadata = $pedagogy_metadata, c.exam_metadata = $exam_metadata,
                     c.field_confidence = $field_confidence, c.sources = $sources
        """
        self.conn.execute(query, parameters=props)

    def insert_relation(self, relation: TypedRelation):
        """Insert a TypedRelation."""
        rel_type = relation.relation_type.value
        props = relation.model_dump(exclude_none=True, exclude={'source_id', 'target_id', 'relation_type'})

        set_clauses = [f"r.{k} = ${k}" for k in props.keys()]
        set_str = "SET " + ", ".join(set_clauses) if set_clauses else ""

        query = f"""
        MATCH (source:Concept {{id: $source_id}})
        MATCH (target:Concept {{id: $target_id}})
        MERGE (source)-[r:{rel_type}]->(target)
        {set_str}
        """
        params = {"source_id": relation.source_id, "target_id": relation.target_id, **props}
        self.conn.execute(query, parameters=params)


class LearnerGraph:
    """Wrapper around Kuzu for the Learner Graph (States and Paths)."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = kuzu.Database(self.db_path)
        self.conn = kuzu.Connection(self.db)
        self._init_schema()

    def _init_schema(self):
        """Initialize the Learner Graph schema if it doesn't exist."""
        tables = self.conn.execute("CALL show_tables() RETURN *;").get_as_df()
        table_names = tables['name'].tolist() if not tables.empty else []

        if "LearnerState" not in table_names:
            _log.info("Creating LearnerState node table in Kuzu")
            # Kuzu only allows one primary key column natively in early versions.
            # Use a concatenated string ID for the primary key.
            self.conn.execute("""
            CREATE NODE TABLE LearnerState (
                id STRING,
                student_id STRING,
                concept_id STRING,
                state STRING,
                mastery DOUBLE,
                confidence DOUBLE,
                calibration_error DOUBLE,
                forgetting_score DOUBLE,
                next_review TIMESTAMP,
                explanation_level STRING,
                active_misconceptions STRING,
                PRIMARY KEY (id)
            );
            """)

        if "HAS_STATE" not in table_names:
            _log.info("Creating HAS_STATE edge table in Kuzu")
            # We don't have a Student node table yet, but we will create a dummy graph edge structure later if required.
            pass
