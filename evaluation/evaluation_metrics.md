# Ground-Truth Evaluation & Metrics Report

This report presents strict exact-span/exact-type metrics alongside semantic/overlap-aware metrics calculated against the human-labeled ground truth dataset in `evaluation/ground_truth.json`.

---

## 1. Overall Performance Metrics

### Token-Level Binary Classification (Accuracy)
- **Evaluation Unit:** Token-level binary classification (PII vs Non-PII) computed across all evaluated benchmark blocks.
- **Normalization:** Overlapping ground-truth annotations were deduplicated/normalized prior to token labeling to properly define the ground-truth population. Tokenization relies on simple whitespace splitting.
- **TP (Actual PII predicted as PII):** 86
- **TN (Actual Non-PII predicted as Non-PII):** 929
- **FP (Actual Non-PII predicted as PII):** 10
- **FN (Actual PII predicted as Non-PII):** 0
- **Accuracy:** 99.0%

### A. Strict Exact-Span Matching
| Metric Mode | Precision | Recall | F1-Score | True Positives | False Positives | False Negatives |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Micro Average** | 87.5% | 82.4% | 84.8% | 28 | 4 | 6 |
| **Macro Average** | 85.4% | 89.2% | 86.4% | - | - | - |

### B. Semantic / Overlap-Aware Matching (One-to-One)
| Metric Mode | Precision | Recall | F1-Score | True Positives | False Positives | False Negatives |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Micro Average** | 90.6% | 85.3% | 87.9% | 29 | 3 | 5 |
| **Macro Average** | 91.0% | 94.8% | 92.0% | - | - | - |

### C. Normalized Semantic Matching (One-to-One Overlap on Deduplicated GT)
| Metric Mode | Precision | Recall | F1-Score | True Positives | False Positives | False Negatives |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Micro Average** | 90.6% | 100.0% | 95.1% | 29 | 3 | 0 |
| **Macro Average** | 91.0% | 100.0% | 94.8% | - | - | - |

> [!NOTE]
> **Strict Exact-Span Matching vs Normalized Semantic Matching**
> * **Strict Exact-Span Matching** answers: *"Did the system reproduce the exact annotated span?"*
>   - In paragraph 24, nested ground-truth annotations of both core and expanded spans (e.g. both `"Registrar of Companies"` and `"Registrar of Companies, Maharashtra"`) are present, yielding 5 artificial FNs because the single predicted authoritative span can only match one of them under strict exact-match rules.
> * **Normalized Semantic Matching** answers: *"Did the system correctly cover the authoritative PII entity?"*
>   - Overlapping nested annotations of the same category are deduplicated, keeping only the longest authoritative entity for evaluation, which resolves the nested span FNs and yields a clean evaluation of actual PII coverage.

---

## 2. Category-Specific Metrics

### A. Strict Exact-Span Metrics
| PII Category | TP | FP | FN | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `ADDRESS` | 2 | 1 | 1 | 66.7% | 66.7% | 66.7% |
| `COMPANY` | 11 | 1 | 5 | 91.7% | 68.8% | 78.6% |
| `EMAIL` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `LOCATION` | 7 | 1 | 0 | 87.5% | 100.0% | 93.3% |
| `PERSON` | 2 | 1 | 0 | 66.7% | 100.0% | 80.0% |
| `PHONE` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |

### B. Semantic / Overlap-Aware Metrics
| PII Category | TP | FP | FN | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `ADDRESS` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `COMPANY` | 11 | 1 | 5 | 91.7% | 68.8% | 78.6% |
| `EMAIL` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `LOCATION` | 7 | 1 | 0 | 87.5% | 100.0% | 93.3% |
| `PERSON` | 2 | 1 | 0 | 66.7% | 100.0% | 80.0% |
| `PHONE` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |

### C. Normalized Semantic Metrics
| PII Category | TP | FP | FN | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `ADDRESS` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `COMPANY` | 11 | 1 | 0 | 91.7% | 100.0% | 95.7% |
| `EMAIL` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `LOCATION` | 7 | 1 | 0 | 87.5% | 100.0% | 93.3% |
| `PERSON` | 2 | 1 | 0 | 66.7% | 100.0% | 80.0% |
| `PHONE` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |

---

## 3. Detailed Error Analysis (Strict Matching)

### Suspected False Positives (Detected but not in Ground Truth)
Total: 4

- **Type**: `COMPANY` | **Text**: `"the General Information Document"` | **Location**: body / paragraph=47
  *Context*: "This Red Herring Prospectus uses certain definitions and abbreviations which, unless the context oth..."
- **Type**: `PERSON` | **Text**: `"Reference Rate"` | **Location**: body / paragraph=133
  *Context*: "Source: FBIL Reference Rate as available on www.fbil.org.in. and www.oanda.com/bvi-en/ Notes:..."
- **Type**: `LOCATION` | **Text**: `"the Supa Facility"` | **Location**: body / paragraph=148
  *Context*: "Any delays or cost overruns in the completion of the construction of the Supa Facility;..."
- **Type**: `ADDRESS` | **Text**: `"3 Inspire BKC G Block, Bandra Kurla Complex"` | **Location**: body / paragraph=754
  *Context*: "801-804, Wing A, Building No. 3 Inspire BKC G Block, Bandra Kurla Complex..."

---

### Suspected False Negatives (PII Missed by Pipeline)
Total: 6

- **Type**: `COMPANY` | **Text**: `"Registrar of Companies"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `ADDRESS` | **Text**: `"3 Inspire BKC G Block, Bandra Kurla Complex"` | **Location**: body / paragraph=754
  *Context*: "801-804, Wing A, Building No. 3 Inspire BKC G Block, Bandra Kurla Complex..."
