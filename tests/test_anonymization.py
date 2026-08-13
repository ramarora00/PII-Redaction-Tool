import pytest
from src.detection.models import PIIEntity
from src.anonymization.generator import SyntheticGenerator
from src.anonymization.entity_store import EntityStore
from src.detection.regex_detector import RegexDetector

def test_alias_merging_and_synthetic_consistency():
    generator = SyntheticGenerator(locale="en_IN")
    store = EntityStore(generator)
    
    cand1 = PIIEntity("PERSON", "Mr. Rajesh Hegde", 0, 16, 0.90, "spacy")
    cand2 = PIIEntity("PERSON", "Rajesh Hegde", 0, 12, 0.90, "presidio")
    
    store.register_candidates([cand1, cand2])
    store.generate_all_replacements()
    
    id1 = store.key_to_id.get("PERSON::rajesh hegde")
    assert id1 is not None
    
    # Assert Mr. Rajesh Hegde and Rajesh Hegde resolve to same ID
    key_with_title = f"PERSON::{store.normalize_name('Mr. Rajesh Hegde')}"
    assert store.key_to_id.get(key_with_title) == id1
    
    # Assert same replacement
    rep1 = store.get_replacement("PERSON", "Mr. Rajesh Hegde")
    rep2 = store.get_replacement("PERSON", "Rajesh Hegde")
    assert rep1 == rep2
    assert len(rep1.split()) >= 2  # generated full name

def test_ambiguous_short_names_split():
    generator = SyntheticGenerator(locale="en_IN")
    store = EntityStore(generator)
    
    # Multiple full names in document
    c_full1 = PIIEntity("PERSON", "Rajesh Hegde", 0, 12, 0.90, "spacy")
    c_full2 = PIIEntity("PERSON", "Rajesh Kumar", 0, 12, 0.90, "spacy")
    c_short = PIIEntity("PERSON", "Rajesh", 0, 6, 0.80, "spacy")
    
    store.register_candidates([c_full1, c_full2, c_short])
    store.generate_all_replacements()
    
    id_full1 = store.key_to_id.get("PERSON::rajesh hegde")
    id_full2 = store.key_to_id.get("PERSON::rajesh kumar")
    id_short = store.key_to_id.get("PERSON::rajesh")
    
    # Since "Rajesh" is ambiguous, it should map to its own unique ID (split), not merge with either full name
    assert id_short != id_full1
    assert id_short != id_full2
    assert store.get_replacement("PERSON", "Rajesh") != store.get_replacement("PERSON", "Rajesh Hegde")

def test_unambiguous_short_name_merge():
    generator = SyntheticGenerator(locale="en_IN")
    store = EntityStore(generator)
    
    # Only one full name Rajesh Hegde
    c_full = PIIEntity("PERSON", "Rajesh Hegde", 0, 12, 0.90, "spacy")
    c_short = PIIEntity("PERSON", "Rajesh", 0, 6, 0.80, "spacy")
    
    store.register_candidates([c_full, c_short])
    store.generate_all_replacements()
    
    id_full = store.key_to_id.get("PERSON::rajesh hegde")
    id_short = store.key_to_id.get("PERSON::rajesh")
    
    # Rajesh should resolve to same ID as Rajesh Hegde
    assert id_short == id_full
    assert store.get_replacement("PERSON", "Rajesh") == store.get_replacement("PERSON", "Rajesh Hegde")

def test_relationship_preservation_email():
    generator = SyntheticGenerator(locale="en_US")
    store = EntityStore(generator)
    
    c_person = PIIEntity("PERSON", "Rajesh Hegde", 0, 12, 0.90, "spacy")
    c_email = PIIEntity("EMAIL", "rajesh.hegde@company.com", 0, 24, 0.99, "regex")
    
    store.register_candidates([c_person, c_email])
    store.generate_all_replacements()
    
    fake_name = store.get_replacement("PERSON", "Rajesh Hegde")
    fake_email = store.get_replacement("EMAIL", "rajesh.hegde@company.com")
    
    # email prefix must align with slugified fake name
    prefix = fake_email.split("@")[0]
    expected_slug = fake_name.lower().replace(" ", ".")
    assert prefix == expected_slug

def test_unlinked_email_generation():
    # If email has no matching name in document, it gets a generic seeded email
    generator = SyntheticGenerator(locale="en_US")
    store = EntityStore(generator)
    
    c_email = PIIEntity("EMAIL", "admin@company.com", 0, 17, 0.99, "regex")
    store.register_candidates([c_email])
    store.generate_all_replacements()
    
    fake_email = store.get_replacement("EMAIL", "admin@company.com")
    assert "@" in fake_email
    assert fake_email != "admin@company.com"

def test_credit_card_validity():
    generator = SyntheticGenerator()
    original_cc = "4111-1111-1111-1111"
    
    # Generate CC replacement
    fake_cc = generator.generate_credit_card("CREDIT_CARD_001", original_cc)
    
    assert len(fake_cc) == len(original_cc)
    assert fake_cc != original_cc
    # Preserves formatting hyphens
    assert fake_cc[4] == "-"
    assert fake_cc[9] == "-"
    assert fake_cc[14] == "-"
    
    # Must be Luhn valid
    clean_digits = fake_cc.replace("-", "")
    assert RegexDetector.is_valid_luhn(clean_digits) is True
    # Ensure it did not preserve BIN prefix (4111)
    assert not fake_cc.startswith("4111")

def test_typed_key_separation():
    generator = SyntheticGenerator()
    store = EntityStore(generator)
    
    # Same value, different PII types
    c_person = PIIEntity("PERSON", "support", 0, 7, 0.90, "spacy")
    c_email = PIIEntity("EMAIL", "support", 0, 7, 0.99, "regex")
    
    store.register_candidates([c_person, c_email])
    
    id_person = store.key_to_id.get("PERSON::support")
    id_email = store.key_to_id.get("EMAIL::support")
    
    assert id_person is not None
    assert id_email is not None
    assert id_person != id_email

def test_seeded_determinism():
    # Multiple stores created with identical config seeds must yield identical values
    gen1 = SyntheticGenerator(locale="en_US")
    store1 = EntityStore(gen1)
    
    gen2 = SyntheticGenerator(locale="en_US")
    store2 = EntityStore(gen2)
    
    cand = PIIEntity("PERSON", "Rajesh Hegde", 0, 12, 0.90, "spacy")
    
    store1.register_candidates([cand])
    store1.generate_all_replacements()
    
    store2.register_candidates([cand])
    store2.generate_all_replacements()
    
    assert store1.get_replacement("PERSON", "Rajesh Hegde") == store2.get_replacement("PERSON", "Rajesh Hegde")

def test_date_formatting_preservation():
    generator = SyntheticGenerator()
    
    orig_dob = "15-05-1990"
    fake_dob = generator.generate_date("DATE_OF_BIRTH_001", orig_dob, is_dob=True)
    assert len(fake_dob) == len(orig_dob)
    assert fake_dob[2] == "-"
    assert fake_dob[5] == "-"
    
    orig_listing = "2026/08/13"
    fake_listing = generator.generate_date("DATE_001", orig_listing, is_dob=False)
    assert len(fake_listing) == len(orig_listing)
    assert fake_listing[4] == "/"
    assert fake_listing[7] == "/"
