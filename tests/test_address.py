import pytest
from src.detection.regex_detector import RegexDetector
from src.detection.fusion import resolve_candidates
from src.detection.models import PIIEntity

def test_address_street_pattern():
    detector = RegexDetector()
    text = "We are located at 123 MG Road, Mumbai, Maharashtra 400001 for business."
    entities = resolve_candidates(text, detector.detect(text))
    
    # Check that ADDRESS was found
    addresses = [e for e in entities if e.entity_type == "ADDRESS"]
    assert len(addresses) == 1
    assert addresses[0].text == "123 MG Road, Mumbai, Maharashtra 400001"

def test_address_registered_office():
    detector = RegexDetector()
    text = "Please contact our Registered Office: 456 Corporate Bhavan, New Delhi, 110001."
    entities = resolve_candidates(text, detector.detect(text))
    
    addresses = [e for e in entities if e.entity_type == "ADDRESS"]
    assert len(addresses) == 1
    assert addresses[0].text == "Registered Office: 456 Corporate Bhavan, New Delhi, 110001"

def test_address_pin_code():
    detector = RegexDetector()
    text = "Send mail to Bangalore, Karnataka 560001 or visit us."
    entities = resolve_candidates(text, detector.detect(text))
    
    addresses = [e for e in entities if e.entity_type == "ADDRESS"]
    assert len(addresses) == 1
    assert addresses[0].text == "Bangalore, Karnataka 560001"

def test_standalone_location_preservation():
    detector = RegexDetector()
    text = "We expanded our business in Maharashtra."
    entities = resolve_candidates(text, detector.detect(text))
    
    addresses = [e for e in entities if e.entity_type == "ADDRESS"]
    assert len(addresses) == 0  # Should NOT be an address

def test_address_vs_location_fusion():
    # Simulate an overlap where Presidio/NER gives LOCATION for "Mumbai" and Regex gives ADDRESS for the whole string.
    text = "123 Example Road, Mumbai, Maharashtra 400001"
    
    cands = [
        PIIEntity(entity_type="LOCATION", text="Mumbai", start=18, end=24, confidence=0.85, source="ner"),
        PIIEntity(entity_type="LOCATION", text="Maharashtra", start=26, end=37, confidence=0.85, source="ner"),
        PIIEntity(entity_type="ADDRESS", text=text, start=0, end=44, confidence=0.90, source="regex")
    ]
    
    resolved = resolve_candidates(text, cands)
    
    # Because ADDRESS has higher TYPE_STRENGTH (2) vs LOCATION (1) and covers the locations, it should win.
    assert len(resolved) == 1
    assert resolved[0].entity_type == "ADDRESS"
    assert resolved[0].text == text

def test_generator_address():
    from src.anonymization.generator import SyntheticGenerator
    generator = SyntheticGenerator()
    addr = generator.generate_address("ADDRESS_001")
    assert addr is not None
    assert "\n" not in addr  # We replaced newlines with commas
