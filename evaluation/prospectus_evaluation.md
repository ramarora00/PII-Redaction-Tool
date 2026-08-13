# Real Prospectus PII Evaluation Report

This report presents quantitative metrics and performance characteristics collected by running the PII redaction pipeline over `data/input/prospectus.docx`.

---

## 1. Execution Profile & Runtime Ratios

| Profiling Category | Duration (seconds) | Percentage of Total Execution |
| :--- | :---: | :---: |
| **Total Evaluation Execution** | 160.7021s | 100.0% |
| Document Loading Time | 0.2852s | 0.2% |
| Regex Detector Time | 0.2700s | 0.2% |
| spaCy NER Detector Time | 70.7086s | 44.0% |
| Presidio Analyzer Time | 80.8894s | 50.3% |
| Fusion Layer Time | 0.1009s | 0.1% |
| Validation Layer Time | 0.0920s | 0.1% |

---

## 2. Document Traversal Summary

| Container Block Type | Scanned Blocks count | Percentage of Document |
| :--- | :---: | :---: |
| **Total Scanned Blocks** | 5375 | 100.0% |
| Body Paragraphs | 1006 | 18.7% |
| Table Cell Paragraphs | 4199 | 78.1% |
| Section Headers | 85 | 1.6% |
| Section Footers | 85 | 1.6% |

---

## 3. Candidate Fusion & Redaction Summary

| Stage Metric | Candidate Count | Summary Description |
| :--- | :---: | :--- |
| **Raw Regex Candidates** | 71 | Candidate matches from structured regex rules. |
| **Raw spaCy NER Candidates** | 3812 | Candidates from spaCy statistical model. |
| **Raw Presidio Candidates** | 1907 | Candidates from Microsoft Presidio engine. |
| **Total Raw Candidates (Inputs)** | 5790 | Sum of all raw hits prior to fusion. |
| **Merged Duplicates & Conflicts** | 760 | Candidates merged or dropped during overlapping deconfliction. |
| **Final Resolved Candidates** | 5030 | Normalized candidates (including generic DATE). |
| **Candidates Rejected by Validator** | 806 | Suspicious false positives filtered by context validator. |
| **Final Redacted PII Spans** | 3263 | Verified PII entities (KEEP candidates). |

---

## 3.1 Candidate Validation Reason Breakdown

| Validation Reason | Suppression Count | Description |
| :--- | :---: | :--- |
| `GENERIC_DOCUMENT_TERM` | 773 | Common nouns / document metadata matching NER. |
| `ADDRESS_CONTEXT` | 32 | Address divisions misclassified as PERSON. |
| `TECHNICAL_STANDARD` | 1 | Technical standard numbers. |
| `FINANCIAL_CONTEXT` | 0 | Numerical currency and scale units. |

---

## 4. Redacted PII Category Distribution

| PII Category | Final Redactions | Percentage of Redactions |
| :--- | :---: | :---: |
| **Total Redacted Spans** | 3263 | 100.0% |
| `PERSON` | 497 | 15.2% |
| `COMPANY` | 2115 | 64.8% |
| `LOCATION` | 533 | 16.3% |
| `EMAIL` | 70 | 2.1% |
| `PHONE` | 48 | 1.5% |
| `ADDRESS` | 0 | 0.0% |
| `SSN` | 0 | 0.0% |
| `CREDIT_CARD` | 0 | 0.0% |
| `IP_ADDRESS` | 0 | 0.0% |
| `DATE_OF_BIRTH` | 0 | 0.0% |

---

## 5. Location Distribution of Redacted Spans

| Location Path Type | Redactions Count | Percentage of Redactions |
| :--- | :---: | :---: |
| **Total Redacted Spans** | 3263 | 100.0% |
| Body Paragraphs | 1018 | 31.2% |
| Table Cell Paragraphs | 2245 | 68.8% |
| Section Headers | 0 | 0.0% |
| Section Footers | 0 | 0.0% |

---

## 6. Representative Diagnostic Examples

```text
Type: COMPANY
Text: KSH INTERNATIONAL LIMITED
Location: body / paragraph=11
Detector: spacy
Final: COMPANY (Reason: GENUINE_PII)
Context: "KSH INTERNATIONAL LIMITED CORPORATE IDENTITY NUMBER: U2..."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: COMPANY
Text: KSH INTERNATIONAL LIMITED
Location: body / paragraph=23
Detector: spacy
Final: COMPANY (Reason: GENUINE_PII)
Context: "KSH INTERNATIONAL LIMITED"
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: COMPANY
Text: Bhandary Metal Extrusion Private Limited
Location: body / paragraph=24
Detector: spacy
Final: COMPANY (Reason: GENUINE_PII)
Context: "...s originally incorporated as “Bhandary Metal Extrusion Private Limited” under the provisions of the ..."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: LOCATION
Text: Bombay
Location: body / paragraph=24
Detector: spacy + presidio
Final: LOCATION (Reason: GENUINE_PII)
Context: "... of Companies, Maharashtra at Bombay. Subsequently, the name of ou..."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: LOCATION
Text: Mumbai
Location: body / paragraph=24
Detector: spacy
Final: LOCATION (Reason: GENUINE_PII)
Context: "...r of Companies Maharashtra at Mumbai pursuant to change of name un..."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: LOCATION
Text: Mumbai
Location: body / paragraph=24
Detector: spacy
Final: LOCATION (Reason: GENUINE_PII)
Context: "... of Companies, Maharashtra at Mumbai to the jurisdiction of the Re..."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: PERSON
Text: Sarthak Malvadkar
Location: body / paragraph=28
Detector: spacy
Final: PERSON (Reason: GENUINE_PII)
Context: "Contact Person: Sarthak Malvadkar, Company Secretary and Compli..."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: PHONE
Text: + 91 20 4505 3237
Location: body / paragraph=28
Detector: presidio
Final: PHONE (Reason: GENUINE_PII)
Context: "...ompliance Officer; Telephone: + 91 20 4505 3237;"
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: EMAIL
Text: cs.connect@kshinternational.com
Location: body / paragraph=29
Detector: regex + presidio
Final: EMAIL (Reason: GENUINE_PII)
Context: "E-mail: cs.connect@kshinternational.com; Website: www.kshinternationa..."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: PERSON
Text: Reference Rate
Location: body / paragraph=133
Detector: spacy
Final: PERSON (Reason: GENUINE_PII)
Context: "Source: FBIL Reference Rate as available on www.fbil.org...."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: PERSON
Text: Kushal Subbayya Hegde
Location: body / paragraph=166
Detector: spacy
Final: PERSON (Reason: GENUINE_PII)
Context: "Kushal Subbayya Hegde, Pushpa Kushal Hegde, Rajesh ..."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: PHONE
Text: + 91 20 45053237
Location: body / paragraph=744
Detector: presidio
Final: PHONE (Reason: GENUINE_PII)
Context: "Telephone: + 91 20 45053237"
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: EMAIL
Text: Sarthak.malvadkar@kshinterantional.com
Location: body / paragraph=745
Detector: regex + spacy + presidio
Final: EMAIL (Reason: GENUINE_PII)
Context: "E-mail: Sarthak.malvadkar@kshinterantional.com"
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: PHONE
Text: +91 22 40094400
Location: body / paragraph=756
Detector: presidio
Final: PHONE (Reason: GENUINE_PII)
Context: "Telephone: +91 22 40094400 Email: ksh.ipo@nuvama.com Web..."
Assessment: SUSPECTED_TRUE_POSITIVE

---

Type: EMAIL
Text: ksh.ipo@nuvama.com
Location: body / paragraph=756
Detector: regex + presidio
Final: EMAIL (Reason: GENUINE_PII)
Context: "...phone: +91 22 40094400 Email: ksh.ipo@nuvama.com Website: www.nuvama.com"
Assessment: SUSPECTED_TRUE_POSITIVE
```

---

## 7. Suspected Findings & Recommendations

### Suspected False Positives
- Numbers representing financial values or application indices incorrectly detected as `PHONE` or `CREDIT_CARD` (e.g. order numbers, folio references).
- General business terms (e.g. "Director", "Chairman", "Promoter") or common nouns incorrectly cataloged by spaCy/Presidio as `PERSON` or `COMPANY`.

### Suspected False Negatives
- Fragmented names across runs that fail dictionary NER checks.
- Address spans missing clean formatting boundaries.

### Architectural Recommendations for Milestone 8 (Tuning)
1. **Financial number suppressions**: Strengthen context rules to exclude sequences following financial abbreviations (e.g. `Rs.`, `Crore`, `Lakh`).
2. **False positive filters**: Implement custom lists to suppress generic nouns matched by NER engines.
