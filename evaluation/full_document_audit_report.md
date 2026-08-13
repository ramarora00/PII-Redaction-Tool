# Full-Document PII Audit Report

This report presents diagnostic profiling statistics and error clusters collected across the entire `prospectus.docx` (scanned 5375 structural blocks).

---

## 1. Document Structure & Coverage Summary
- **Scanned Blocks by Container**:
  - Body Paragraphs: 1006
  - Table Cell Paragraphs: 4199
  - Section Headers: 85
  - Section Footers: 85

- **Validated (KEPT) PII Entities by Type**:
  - `COMPANY`: 1954
  - `LOCATION`: 467
  - `PERSON`: 469
  - `PHONE`: 48
  - `EMAIL`: 70

- **Validated (REJECTED) PII Entities by Type**:
  - `COMPANY`: 689
  - `PERSON`: 362
  - `LOCATION`: 28
  - `PHONE`: 1

---

## 2. Cross-Detector Disagreement Analysis
This table shows kept candidate counts matching each unique combination of detector source provenance.

| Detector Combination | Count |
| :--- | :---: |
| spacy | 2005 |
| presidio + spacy | 518 |
| presidio | 209 |
| regex + spacy | 124 |
| presidio + regex + spacy | 81 |
| presidio + regex | 40 |
| regex | 31 |

---

## 3. False Positive Clustering (Validator Rejections)
Candidates rejected by the validation layer clustered by rejection pattern:

| Rejection Reason | Total Rejections | Sample Cluster Items (Count) |
| :--- | :---: | :--- |
| `GENERIC_DOCUMENT_TERM` | 1046 | "Offer" (257), "the Promoter Selling Shareholders" (76), "Promoters" (51), "the Offer Price" (48), "OFFER" (41), "Anchor Investors" (40), "Company" (29), "Prospectus" (29), "the Bid/Offer Period" (27), "Board" (26) |
| `ADDRESS_CONTEXT` | 33 | "Chakan Taluka - Khed" (4), "Appasaheb Marathe Marg," (4), "Vikhroli" (3), "Kanjurmarg" (3), "Deccan Gymkhana" (3), "Taluka Khed" (2), "Shivaji Nagar" (2), "Bandra Kurla Complex" (2), "Mauje Palve Khurd" (1), "Taluka Parner" (1) |
| `TECHNICAL_STANDARD` | 1 | "16949" (1) |

---

## 4. Discovered Heuristic FNs (Missed PII Search)
The following potential PII elements matched name/structure heuristics but were not detected by the pipeline.

Total Discovered Heuristic FNs: 0

| Entity Type | Discovered Text | Location Block | Sentence Context |
| :--- | :--- | :--- | :--- |

