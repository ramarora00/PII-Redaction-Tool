# End-to-End Redaction Assurance Report

This report presents verification outcomes of the structural integrity checks and deep zero-leak PII validation performed on the redacted output document `data/output/prospectus_redacted.docx`.

---

## 1. Structural Integrity Verification

| Document Component | Original Count | Redacted Count | Match Status |
| :--- | :---: | :---: | :---: |
| **Body Paragraphs** | 1006 | 1006 | PASSED |
| **Tables** | 76 | 76 | PASSED |
| **Table Cells** | 3722 | 3722 | PASSED |
| **Sections** | 85 | 85 | PASSED |
| **Header Paragraphs** | 85 | 85 | PASSED |
| **Footer Paragraphs** | 85 | 85 | PASSED |

- **Overall Structural Preservation Status**: **PASSED**

---

## 2. PII Zero-Leak Verification

### Overall Status: **PASSED**

---

### Tier 1 — Critical PII Global Search (PERSON, EMAIL, PHONE, SSN, CREDIT_CARD, IP_ADDRESS, DATE_OF_BIRTH)

Every original value of a critical PII entity is searched across the **entire** redacted document.
Any occurrence is a **failure** — these values must never survive redaction.

- **Entities Checked**: 178
- **Leaks Found**: 0
- **Status**: **PASSED**

*No critical PII leaks detected.*

---

### Tier 2 — Contextual Entity Span Verification (COMPANY, LOCATION)

For each COMPANY/LOCATION entity that was selected for redaction, the checker verifies:
1. The **original text** no longer appears in its **specific source paragraph**.
2. The **synthetic replacement** now appears in that paragraph instead.

This avoids false positives from legitimate unrelated occurrences of the same term elsewhere.

- **Redaction Spans Verified**: 1953
- **Span Verification Failures**: 0
- **Status**: **PASSED**

*All contextual entity redactions verified at their source spans.*

---

## 3. Redaction Manifest Summary

- **Total Redactions Applied**: 2367
- **Critical PII Redactions**: 414
- **Contextual Entity Redactions**: 1953
