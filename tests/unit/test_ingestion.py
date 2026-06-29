import pytest
from agents.ingestion.chunker import chunk_markdown
from agents.ingestion.ontology_mapper import OntologyMapper
from agents.ingestion.validator import Validator
from core.types.schemas import ConceptObject, SourceRef

def test_chunker():
    md = """
# Chapter 1
Some intro text.
## 1.1 Bookkeeping
This is about bookkeeping. It is very important.
""" * 10
    chunks = chunk_markdown(md, "test.md", max_tokens=20)
    assert len(chunks) > 0
    assert chunks[0].heading_path.startswith("Chapter 1")

def test_ontology_mapper():
    mapper = OntologyMapper()
    assert mapper.get_canonical_name("book keeping") == "Bookkeeping"
    assert mapper.generate_id("Bookkeeping") == "com11_acc_bookkeeping_v1"

def test_validator():
    validator = Validator(confidence_threshold=0.8)
    source = SourceRef(file_name="t", heading_path="H", chunk_index=0)
    c1 = ConceptObject(
        id="c1", name="C1", subject="Math", grade=11, confidence_score=0.9,
        definition="D1", intuition="I1", sources=[source]
    )
    c2 = ConceptObject(
        id="c2", name="C2", subject="Math", grade=11, confidence_score=0.5,
        definition="D2", intuition="I2", sources=[source]
    )
    valid_c, valid_r = validator.validate([c1, c2], [])
    assert len(valid_c) == 1
    assert valid_c[0].id == "c1"
