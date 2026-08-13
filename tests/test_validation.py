import pytest
from src.detection.models import PIIEntity
from src.detection.validation import CandidateValidator

def test_validation_near_misses_and_suppressions():
    validator = CandidateValidator()

    # 1. Contact Person: Sarthak Malvadkar -> KEEP PERSON
    text1 = "Contact Person: Sarthak Malvadkar is here."
    cand1 = PIIEntity("PERSON", "Sarthak Malvadkar", 16, 33, 0.95, "spacy")
    res1 = validator.validate_candidates(text1, [cand1])
    assert res1[0].metadata["validation_decision"] == "KEEP"
    assert res1[0].metadata["validation_reason"] == "GENUINE_PII"

    # 2. Email: sarthak.malvadkar@company.com -> KEEP EMAIL (No rule should suppress emails)
    text2 = "Email: sarthak.malvadkar@company.com"
    cand2 = PIIEntity("EMAIL", "sarthak.malvadkar@company.com", 7, 36, 0.99, "regex")
    res2 = validator.validate_candidates(text2, [cand2])
    assert res2[0].metadata["validation_decision"] == "KEEP"

    # 3. IATF 16949:2016 -> REJECT PHONE
    text3 = "certification for IATF 16949:2016 standard."
    cand3 = PIIEntity("PHONE", "16949", 23, 28, 0.85, "presidio")
    res3 = validator.validate_candidates(text3, [cand3])
    assert res3[0].metadata["validation_decision"] == "REJECT"
    assert res3[0].metadata["validation_reason"] == "TECHNICAL_STANDARD"

    # 4. Telephone: +91 20 45053237 -> KEEP PHONE
    text4 = "Telephone: +91 20 45053237"
    cand4 = PIIEntity("PHONE", "+91 20 45053237", 11, 26, 0.90, "presidio")
    res4 = validator.validate_candidates(text4, [cand4])
    assert res4[0].metadata["validation_decision"] == "KEEP"

    # 5. Rs. 10,00,000 -> REJECT PHONE (financial context)
    text5 = "Total assets are Rs. 10,00,000"
    cand5 = PIIEntity("PHONE", "10,00,000", 21, 30, 0.80, "presidio")
    res5 = validator.validate_candidates(text5, [cand5])
    assert res5[0].metadata["validation_decision"] == "REJECT"
    assert res5[0].metadata["validation_reason"] == "FINANCIAL_CONTEXT"

    # 6. Village Birdewadi, Chakan Taluka - Khed -> REJECT PERSON on Chakan Taluka - Khed
    text6 = "Address is Village Birdewadi, Chakan Taluka - Khed, Pune."
    cand6 = PIIEntity("PERSON", "Chakan Taluka - Khed", 30, 50, 0.80, "spacy")
    res6 = validator.validate_candidates(text6, [cand6])
    assert res6[0].metadata["validation_decision"] == "REJECT"
    assert res6[0].metadata["validation_reason"] == "ADDRESS_CONTEXT"

    # 7. Mr. Offer Sharma -> KEEP PERSON (generic term with personal title prefix)
    text7 = "Please speak to Mr. Offer Sharma."
    cand7 = PIIEntity("PERSON", "Offer", 20, 25, 0.90, "spacy")
    res7 = validator.validate_candidates(text7, [cand7])
    assert res7[0].metadata["validation_decision"] == "KEEP"

    # 8. Offer related terms -> REJECT PERSON
    text8 = "The Offer related terms used herein..."
    cand8 = PIIEntity("PERSON", "Offer", 4, 9, 0.90, "spacy")
    res8 = validator.validate_candidates(text8, [cand8])
    assert res8[0].metadata["validation_decision"] == "REJECT"
    assert res8[0].metadata["validation_reason"] == "GENERIC_DOCUMENT_TERM"

    # 9. Sarthak Malvadkar, Mumbai -> KEEP PERSON (location name alone does not suppress)
    text9 = "Sarthak Malvadkar, Mumbai"
    cand9 = PIIEntity("PERSON", "Sarthak Malvadkar", 0, 17, 0.95, "spacy")
    res9 = validator.validate_candidates(text9, [cand9])
    assert res9[0].metadata["validation_decision"] == "KEEP"

    # 10. Standard 9876543210 -> KEEP PHONE
    text10 = "Standard 9876543210 is standard phone."
    cand10 = PIIEntity("PHONE", "9876543210", 9, 19, 0.90, "presidio")
    res10 = validator.validate_candidates(text10, [cand10])
    assert res10[0].metadata["validation_decision"] == "KEEP"

    # 11. SCRR regulatory acronym -> REJECT PERSON
    text11 = "compliance under the SCRR regulations."
    cand11 = PIIEntity("PERSON", "SCRR", 21, 25, 0.80, "presidio")
    res11 = validator.validate_candidates(text11, [cand11])
    assert res11[0].metadata["validation_decision"] == "REJECT"
    assert res11[0].metadata["validation_reason"] == "GENERIC_DOCUMENT_TERM"

    # 12. our Directors -> REJECT PERSON
    text12 = "This affects our Directors."
    cand12 = PIIEntity("PERSON", "Directors", 17, 26, 0.85, "spacy")
    res12 = validator.validate_candidates(text12, [cand12])
    assert res12[0].metadata["validation_decision"] == "REJECT"
    assert res12[0].metadata["validation_reason"] == "GENERIC_DOCUMENT_TERM"

    # 13. Director Rajesh Hegde -> KEEP (Directors is part of a larger name structure)
    text13 = "Director Rajesh Hegde is present."
    cand13 = PIIEntity("PERSON", "Director Rajesh Hegde", 0, 21, 0.95, "spacy")
    res13 = validator.validate_candidates(text13, [cand13])
    assert res13[0].metadata["validation_decision"] == "KEEP"

