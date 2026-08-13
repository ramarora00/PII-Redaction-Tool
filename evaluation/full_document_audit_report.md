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
  - `COMPANY`: 1919
  - `LOCATION`: 485
  - `PERSON`: 479
  - `PHONE`: 48
  - `EMAIL`: 70

- **Validated (REJECTED) PII Entities by Type**:
  - `COMPANY`: 687
  - `PERSON`: 362
  - `LOCATION`: 28
  - `PHONE`: 1

---

## 2. Cross-Detector Disagreement Analysis
This table shows kept candidate counts matching each unique combination of detector source provenance.

| Detector Combination | Count |
| :--- | :---: |
| spacy | 2137 |
| presidio + spacy | 533 |
| presidio | 212 |
| presidio + regex + spacy | 63 |
| presidio + regex | 40 |
| regex | 12 |
| regex + spacy | 4 |

---

## 3. False Positive Clustering (Validator Rejections)
Candidates rejected by the validation layer clustered by rejection pattern:

| Rejection Reason | Total Rejections | Sample Cluster Items (Count) |
| :--- | :---: | :--- |
| `GENERIC_DOCUMENT_TERM` | 1044 | "Offer" (257), "the Promoter Selling Shareholders" (76), "Promoters" (51), "the Offer Price" (48), "OFFER" (41), "Anchor Investors" (40), "Company" (29), "Prospectus" (29), "the Bid/Offer Period" (27), "Board" (26) |
| `ADDRESS_CONTEXT` | 33 | "Chakan Taluka - Khed" (4), "Appasaheb Marathe Marg," (4), "Vikhroli" (3), "Kanjurmarg" (3), "Deccan Gymkhana" (3), "Taluka Khed" (2), "Shivaji Nagar" (2), "Bandra Kurla Complex" (2), "Mauje Palve Khurd" (1), "Taluka Parner" (1) |
| `TECHNICAL_STANDARD` | 1 | "16949" (1) |

---

## 4. Discovered Heuristic FNs (Missed PII Search)
The following potential PII elements matched name/structure heuristics but were not detected by the pipeline.

Total Discovered Heuristic FNs: 25

| Entity Type | Discovered Text | Location Block | Sentence Context |
| :--- | :--- | :--- | :--- |
| `COMPANY` | `"Advisory Private Limited"` | `body / paragraph=114` | "...repared by CARE Analytics and Advisory Private Limited (“CareEdge Research”), which..." |
| `COMPANY` | `"Advisory Private Limited"` | `body / paragraph=306` | "...issued by Care Analytics and Advisory Private Limited pursuant to an engagement let..." |
| `COMPANY` | `"Industrial Solutions Limited"` | `body / paragraph=319` | "...Bijlee Limited; CG Power and Industrial Solutions Limited; Emirates Transformer & Switc..." |
| `COMPANY` | `"Advisory Private Limited"` | `body / paragraph=463` | "...repared by Care Analytics and Advisory Private Limited (“CareEdge Research”). All su..." |
| `COMPANY` | `"KSH Infra Park VI Private Limited"` | `body / paragraph=647` | "...Park 5 Private Limited; (iv) KSH Infra Park VI Private Limited; (v) KSH Distriparks Private..." |
| `COMPANY` | `"Company KSH International Limited"` | `body / paragraph=718` | "...Registered Office of our Company KSH International Limited..." |
| `COMPANY` | `"Company KSH International Limited"` | `body / paragraph=723` | "...Corporate Office of our Company KSH International Limited..." |
| `COMPANY` | `"ICICI Securities Limited"` | `body / paragraph=761` | "...ICICI Securities Limited ICICI Venture House Appasaheb..." |
| `COMPANY` | `"ICICI Securities Limited"` | `body / paragraph=785` | "...ICICI Securities Limited ICICI Venture House Appasaheb..." |
| `COMPANY` | `"Formerly Link Intime India Private Limited"` | `body / paragraph=800` | "...Intime India Private Limited (Formerly Link Intime India Private Limited) C-101, Embassy 247..." |
| `COMPANY` | `"ICICI	Securities Limited"` | `table / table=1 / row=8 / cell=1 / paragraph=1` | "...ICICI	Securities Limited..." |
| `COMPANY` | `"ICICI	Securities Limited"` | `table / table=1 / row=8 / cell=2 / paragraph=1` | "...ICICI	Securities Limited..." |
| `COMPANY` | `"Formerly Link Intime India Private Limited"` | `table / table=1 / row=11 / cell=0 / paragraph=1` | "...(Formerly Link Intime India Private Limited)..." |
| `COMPANY` | `"ICICI Securities Limited"` | `table / table=2 / row=14 / cell=2 / paragraph=0` | "...ICICI Securities Limited..." |
| `COMPANY` | `"ICICI Securities Limited"` | `table / table=2 / row=14 / cell=3 / paragraph=0` | "...ICICI Securities Limited..." |
| `COMPANY` | `"ICICI Securities Limited"` | `table / table=2 / row=14 / cell=4 / paragraph=0` | "...ICICI Securities Limited..." |
| `COMPANY` | `"ICICI Securities Limited"` | `table / table=2 / row=14 / cell=5 / paragraph=0` | "...ICICI Securities Limited..." |
| `COMPANY` | `"Formerly Link Intime India Private Limited"` | `table / table=2 / row=14 / cell=6 / paragraph=1` | "...(Formerly Link Intime India Private Limited)..." |
| `COMPANY` | `"Formerly Link Intime India Private Limited"` | `table / table=2 / row=14 / cell=7 / paragraph=1` | "...(Formerly Link Intime India Private Limited)..." |
| `COMPANY` | `"Advisory Private Limited"` | `table / table=5 / row=13 / cell=1 / paragraph=0` | "...der being, CARE Analytics and Advisory Private Limited..." |
| `COMPANY` | `"ICICI Securities Limited"` | `table / table=9 / row=6 / cell=1 / paragraph=0` | "...Wealth Management Limited and ICICI Securities Limited..." |
| `COMPANY` | `"ICICI Securities Limited"` | `table / table=10 / row=18 / cell=1 / paragraph=0` | "...ICICI Securities Limited..." |
| `COMPANY` | `"Formerly Link Intime India Private Limited"` | `table / table=12 / row=7 / cell=1 / paragraph=0` | "...Intime India Private Limited (Formerly Link Intime India Private Limited)..." |
| `COMPANY` | `"Formerly Link Intime India Private Limited"` | `table / table=12 / row=13 / cell=1 / paragraph=0` | "...Intime India Private Limited (Formerly Link Intime India Private Limited)..." |
| `COMPANY` | `"ICICI Securities Limited"` | `table / table=12 / row=20 / cell=1 / paragraph=1` | "...Wealth Management Limited and ICICI Securities Limited..." |
