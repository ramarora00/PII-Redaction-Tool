import pytest
import spacy
from src.detection.models import PIIEntity
from src.detection.regex_detector import RegexDetector
from src.detection.ner_detector import NERDetector
from src.detection.presidio_detector import PresidioDetector

# Check if spaCy English model is available
try:
    spacy.load("en_core_web_sm")
    HAS_SPACY_MODEL = True
except Exception:
    HAS_SPACY_MODEL = False

# ==============================================================================
# DETERMINISTIC REGEX DETECTOR TESTS (No external models required)
# ==============================================================================

def test_regex_email():
    detector = RegexDetector()
    text = "Please reach out to support@example.com for help."
    results = detector.detect(text)
    
    emails = [e for e in results if e.entity_type == "EMAIL"]
    assert len(emails) == 1
    assert emails[0].text == "support@example.com"
    assert emails[0].start == 20
    assert emails[0].end == 39
    assert text[emails[0].start:emails[0].end] == "support@example.com"


def test_regex_phone_positive_and_negative():
    detector = RegexDetector()
    
    # Positive case
    text_pos = "Call me at +91 9876543210 or 123-456-7890."
    results_pos = detector.detect(text_pos)
    phones = [e for e in results_pos if e.entity_type == "PHONE_CANDIDATE"]
    assert len(phones) == 2
    assert "+91 9876543210" in [p.text for p in phones]
    assert "123-456-7890" in [p.text for p in phones]
    
    # Span verification
    for p in phones:
        assert text_pos[p.start:p.end] == p.text

    # Negative precision cases (should be suppressed by surrounding context keywords)
    negative_contexts = [
        "Order No: 9876543210",
        "Reference No: 9876543210",
        "Application No: 9876543210",
        "Invoice No: 9876543210",
        "Ticket No: 9876543210",
        "Page No: 9876543210",
        "Folio No: 9876543210"
    ]
    for text_neg in negative_contexts:
        results_neg = detector.detect(text_neg)
        phones_neg = [e for e in results_neg if e.entity_type == "PHONE_CANDIDATE"]
        assert len(phones_neg) == 0, f"Expected suppression of phone for: {text_neg}"

def test_regex_ssn():
    detector = RegexDetector()
    text = "The SSN is 000-12-3456."
    results = detector.detect(text)
    
    ssns = [e for e in results if e.entity_type == "SSN_CANDIDATE"]
    assert len(ssns) == 1
    assert ssns[0].text == "000-12-3456"
    assert text[ssns[0].start:ssns[0].end] == "000-12-3456"

def test_regex_credit_card():
    detector = RegexDetector()
    
    # Valid Visa card (Luhn checks should pass)
    # 4111-1111-1111-1111 is a known valid Luhn card
    text_valid = "Use credit card: 4111-1111-1111-1111"
    results_valid = detector.detect(text_valid)
    cc_valid = [e for e in results_valid if e.entity_type == "CREDIT_CARD_CANDIDATE"]
    assert len(cc_valid) == 1
    assert cc_valid[0].text == "4111-1111-1111-1111"
    
    # Invalid card (Luhn checks should fail)
    text_invalid = "Use card: 4111-1111-1111-1112"
    results_invalid = detector.detect(text_invalid)
    cc_invalid = [e for e in results_invalid if e.entity_type == "CREDIT_CARD_CANDIDATE"]
    assert len(cc_invalid) == 0

def test_regex_ip():
    detector = RegexDetector()
    
    # IPv4
    text_v4 = "Connection from 192.168.1.254 on port 80."
    results_v4 = detector.detect(text_v4)
    ips_v4 = [e for e in results_v4 if e.entity_type == "IP_CANDIDATE"]
    assert len(ips_v4) == 1
    assert ips_v4[0].text == "192.168.1.254"
    
    # IPv6
    text_v6 = "IPv6 address is 2001:db8:0:0:0:0:2:1"
    # Note: Simplified ipv6 regex looks for 8 parts
    # 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    text_v6_full = "IPv6 is 2001:0db8:85a3:0000:0000:8a2e:0370:7334"
    results_v6 = detector.detect(text_v6_full)
    ips_v6 = [e for e in results_v6 if e.entity_type == "IP_CANDIDATE"]
    assert len(ips_v6) == 1
    assert ips_v6[0].text == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

def test_regex_dates_context():
    detector = RegexDetector()
    
    # Positive DOB context cases
    dob_texts = [
        "Date of Birth: 01-02-2000",
        "DOB: 12/25/1995",
        "Birth Date is 1990/05/15",
        "He was born on 10.10.1985"
    ]
    for text in dob_texts:
        results = detector.detect(text)
        dob = [e for e in results if e.entity_type == "DATE_OF_BIRTH"]
        assert len(dob) == 1, f"Expected DATE_OF_BIRTH for text: {text}"
        assert text[dob[0].start:dob[0].end] == dob[0].text
        
    # Negative date context cases (should remain DATE_CANDIDATE, not DATE_OF_BIRTH)
    generic_texts = [
        "Date of Filing: 01-02-2026",
        "Date of Issue: 12/25/2025",
        "Date of Allotment: 1990/05/15",
        "Date of Listing: 10.10.2024"
    ]
    for text in generic_texts:
        results = detector.detect(text)
        dob = [e for e in results if e.entity_type == "DATE_OF_BIRTH"]
        generic = [e for e in results if e.entity_type == "DATE_CANDIDATE"]
        assert len(dob) == 0, f"Expected NO DATE_OF_BIRTH for text: {text}"
        assert len(generic) == 1, f"Expected DATE_CANDIDATE for text: {text}"
        assert text[generic[0].start:generic[0].end] == generic[0].text

# ==============================================================================
# MODEL DEPENDENT TESTS (Require spaCy and Presidio with en_core_web_sm)
# ==============================================================================

@pytest.mark.skipif(not HAS_SPACY_MODEL, reason="spaCy model 'en_core_web_sm' is not installed.")
def test_ner_detector_candidates():
    detector = NERDetector()
    text = "Mr. John Smith was appointed to the board of Oracle Corporation in London."
    results = detector.detect(text)
    
    persons = [e for e in results if e.entity_type == "PERSON_CANDIDATE"]
    companies = [e for e in results if e.entity_type == "COMPANY_CANDIDATE"]
    locations = [e for e in results if e.entity_type == "LOCATION_CANDIDATE"]
    
    assert len(persons) >= 1
    assert any("John Smith" in p.text for p in persons)
    
    assert len(companies) >= 1
    assert any("Oracle" in c.text for c in companies)
    
    assert len(locations) >= 1
    assert any("London" in l.text for l in locations)
    
    # Span verification
    for ent in results:
        assert text[ent.start:ent.end] == ent.text

@pytest.mark.skipif(not HAS_SPACY_MODEL, reason="spaCy model 'en_core_web_sm' is not installed.")
def test_presidio_detector_candidates():
    detector = PresidioDetector()
    text = "Contact Alice at alice@company.com or +1 (555) 019-2834."
    results = detector.detect(text)
    
    persons = [e for e in results if e.entity_type == "PERSON_CANDIDATE"]
    emails = [e for e in results if e.entity_type == "EMAIL"]
    phones = [e for e in results if e.entity_type == "PHONE_CANDIDATE"]
    
    assert len(persons) >= 1
    assert any("Alice" in p.text for p in persons)
    
    assert len(emails) == 1
    assert emails[0].text == "alice@company.com"
    
    assert len(phones) >= 1
    assert any("555" in p.text for p in phones)
    
    # Span verification
    for ent in results:
        assert text[ent.start:ent.end] == ent.text

@pytest.mark.skipif(not HAS_SPACY_MODEL, reason="spaCy model 'en_core_web_sm' is not installed.")
def test_duplicate_candidate_preservation():
    # If Regex and Presidio both run, they should both preserve their respective PIIEntity outputs
    # without conflict resolution or merging at this stage.
    regex_det = RegexDetector()
    presidio_det = PresidioDetector()
    
    text = "Send credentials to support@company.com."
    
    regex_res = regex_det.detect(text)
    presidio_res = presidio_det.detect(text)
    
    combined = regex_res + presidio_res
    
    # Assert email was found by both
    emails = [e for e in combined if e.entity_type == "EMAIL"]
    assert len(emails) >= 2
    sources = [e.source for e in emails]
    assert "regex" in sources
    assert "presidio" in sources

def test_regex_registries():
    detector = RegexDetector()
    text = "decided by Registrar of Companies, Maharashtra at Mumbai or Registrar of Companies Maharashtra or ROC or RoC."
    results = detector.detect(text)
    
    companies = [c for c in results if c.entity_type == "COMPANY_CANDIDATE"]
    texts = [c.text for c in companies]
    assert "Registrar of Companies, Maharashtra" in texts
    assert "Registrar of Companies Maharashtra" in texts
    assert "ROC" in texts
    assert "RoC" in texts
    for c in companies:
        assert text[c.start:c.end] == c.text
