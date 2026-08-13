import pytest
from src.detection.models import PIIEntity
from src.detection.regex_detector import RegexDetector
from src.detection.fusion import resolve_candidates, are_compatible, should_override

def test_exact_compatible_duplicates_merging():
    text = "Send mail to support@example.com."
    cand1 = PIIEntity(
        entity_type="EMAIL",
        text="support@example.com",
        start=13,
        end=32,
        confidence=0.98,
        source="regex"
    )
    cand2 = PIIEntity(
        entity_type="EMAIL_ADDRESS",
        text="support@example.com",
        start=13,
        end=32,
        confidence=0.85,
        source="presidio"
    )
    
    resolved = resolve_candidates(text, [cand1, cand2])
    assert len(resolved) == 1
    res = resolved[0]
    
    assert res.entity_type == "EMAIL"
    assert res.start == 13
    assert res.end == 32
    assert res.confidence == 0.98
    assert res.source == "fusion"
    
    # Verify provenance metadata
    sources = res.metadata.get("sources", [])
    assert len(sources) == 2
    sources_dict = {s["source"]: s for s in sources}
    assert "regex" in sources_dict
    assert "presidio" in sources_dict
    assert sources_dict["regex"]["confidence"] == 0.98
    assert sources_dict["regex"]["original_type"] == "EMAIL"

def test_incompatible_same_span_resolution():
    text = "Find AcmeCorp here."
    # AcmeCorp [5:13] matched as COMPANY_CANDIDATE (strength 1) and IP_CANDIDATE (strength 3)
    cand_company = PIIEntity(
        entity_type="COMPANY_CANDIDATE",
        text="AcmeCorp",
        start=5,
        end=13,
        confidence=0.70,
        source="spacy"
    )
    cand_ip = PIIEntity(
        entity_type="IP_CANDIDATE",
        text="AcmeCorp",
        start=5,
        end=13,
        confidence=0.90,
        source="regex"
    )
    
    resolved = resolve_candidates(text, [cand_company, cand_ip])
    assert len(resolved) == 1
    # IP wins due to higher semantic strength
    assert resolved[0].entity_type == "IP_ADDRESS"
    assert resolved[0].confidence == 0.90

def test_nested_email_person_conflict():
    text = "Email is john@example.com."
    # nested PERSON: "john" [9:13], EMAIL: "john@example.com" [9:25]
    cand_person = PIIEntity(
        entity_type="PERSON_CANDIDATE",
        text="john",
        start=9,
        end=13,
        confidence=0.80,
        source="spacy"
    )
    cand_email = PIIEntity(
        entity_type="EMAIL",
        text="john@example.com",
        start=9,
        end=25,
        confidence=0.99,
        source="regex"
    )
    
    resolved = resolve_candidates(text, [cand_person, cand_email])
    assert len(resolved) == 1
    # EMAIL is semantically stronger, so it overrides the nested PERSON candidate
    assert resolved[0].entity_type == "EMAIL"
    assert resolved[0].text == "john@example.com"

def test_nested_person_location_compatible_larger_span_wins():
    text = "The Whole-time Director Rajesh Hegde is present."
    # nested PERSON: "Rajesh" [24:30], larger PERSON: "Rajesh Hegde" [24:36]
    cand_short = PIIEntity(
        entity_type="PERSON_CANDIDATE",
        text="Rajesh",
        start=24,
        end=30,
        confidence=0.80,
        source="spacy"
    )
    cand_long = PIIEntity(
        entity_type="PERSON",
        text="Rajesh Hegde",
        start=24,
        end=36,
        confidence=0.85,
        source="presidio"
    )
    
    resolved = resolve_candidates(text, [cand_short, cand_long])
    assert len(resolved) == 1
    # Compatible types, larger span wins
    assert resolved[0].text == "Rajesh Hegde"

def test_dob_vs_generic_date():
    text = "Date of Birth: 01-02-2000"
    # DATE_OF_BIRTH [15:25] and generic DATE_CANDIDATE [15:25]
    cand_dob = PIIEntity(
        entity_type="DATE_OF_BIRTH",
        text="01-02-2000",
        start=15,
        end=25,
        confidence=0.90,
        source="regex"
    )
    cand_generic = PIIEntity(
        entity_type="DATE_CANDIDATE",
        text="01-02-2000",
        start=15,
        end=25,
        confidence=0.50,
        source="regex"
    )
    
    resolved = resolve_candidates(text, [cand_dob, cand_generic])
    assert len(resolved) == 1
    # Contextual elevation DATE_OF_BIRTH wins
    assert resolved[0].entity_type == "DATE_OF_BIRTH"

def test_e2e_phone_suppression():
    detector = RegexDetector()
    text = "Order No: 9876543210 is processed."
    
    # Detect candidates
    candidates = detector.detect(text)
    # The phone number should be suppressed at the detector layer because of "Order No"
    phones = [c for c in candidates if c.entity_type == "PHONE_CANDIDATE"]
    assert len(phones) == 0
    
    # Resolve
    resolved = resolve_candidates(text, candidates)
    # Phone should not survive end-to-end
    final_phones = [r for r in resolved if r.entity_type == "PHONE"]
    assert len(final_phones) == 0

def test_safety_invariant_violations():
    text = "Hello world."
    
    # Out of bounds start/end
    invalid_span = PIIEntity(
        entity_type="PERSON",
        text="Hello",
        start=0,
        end=25, # Out of bounds
        confidence=0.80,
        source="spacy"
    )
    with pytest.raises(ValueError, match="Invalid offsets"):
        resolve_candidates(text, [invalid_span])
        
    # Text mismatch
    mismatch_span = PIIEntity(
        entity_type="PERSON",
        text="world",
        start=0,
        end=5, # "Hello" at [0:5], not "world"
        confidence=0.80,
        source="spacy"
    )
    with pytest.raises(ValueError, match="Candidate text mismatch"):
        resolve_candidates(text, [mismatch_span])

def test_deterministic_ordering():
    text = "Alice and Bob went to London."
    cand_bob = PIIEntity(
        entity_type="PERSON_CANDIDATE",
        text="Bob",
        start=10,
        end=13,
        confidence=0.80,
        source="spacy"
    )
    cand_alice = PIIEntity(
        entity_type="PERSON_CANDIDATE",
        text="Alice",
        start=0,
        end=5,
        confidence=0.80,
        source="spacy"
    )
    
    resolved = resolve_candidates(text, [cand_bob, cand_alice])
    assert len(resolved) == 2
    # Verify sorted order (Alice at 0 comes first, then Bob at 10)
    assert resolved[0].text == "Alice"
    assert resolved[1].text == "Bob"

def test_empty_candidates():
    assert resolve_candidates("Hello", []) == []

def test_multiple_unrelated_entities():
    text = "Send mail to support@example.com or call 123-456-7890."
    cand_email = PIIEntity(
        entity_type="EMAIL",
        text="support@example.com",
        start=13,
        end=32,
        confidence=0.98,
        source="regex"
    )
    cand_phone = PIIEntity(
        entity_type="PHONE_CANDIDATE",
        text="123-456-7890",
        start=41,
        end=53,
        confidence=0.85,
        source="regex"
    )
    
    resolved = resolve_candidates(text, [cand_email, cand_phone])
    assert len(resolved) == 2
    assert resolved[0].entity_type == "EMAIL"
    assert resolved[1].entity_type == "PHONE"
