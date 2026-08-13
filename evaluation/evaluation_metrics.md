# Ground-Truth Evaluation & Metrics Report

This report presents strict exact-span/exact-type metrics calculated against the human-labeled ground truth dataset in `evaluation/ground_truth.json`.

---

## 1. Overall Performance Metrics

| Metric Mode | Precision | Recall | F1-Score | True Positives | False Positives | False Negatives |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Micro Average** | 89.3% | 80.6% | 84.7% | 25 | 3 | 6 |
| **Macro Average** | 88.8% | 90.9% | 88.9% | - | - | - |

---

## 2. Category-Specific Metrics

| PII Category | TP | FP | FN | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `COMPANY` | 11 | 1 | 5 | 91.7% | 68.8% | 78.6% |
| `EMAIL` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `LOCATION` | 6 | 1 | 1 | 85.7% | 85.7% | 85.7% |
| `PERSON` | 2 | 1 | 0 | 66.7% | 100.0% | 80.0% |
| `PHONE` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |

---

## 3. Detailed Error Analysis

### Suspected False Positives (Detected but not in Ground Truth)
Total: 3

- **Type**: `COMPANY` | **Text**: `"the General Information Document"` | **Location**: body / paragraph=47
  *Context*: "This Red Herring Prospectus uses certain definitions and abbreviations which, unless the context oth..."
- **Type**: `PERSON` | **Text**: `"Reference Rate"` | **Location**: body / paragraph=133
  *Context*: "Source: FBIL Reference Rate as available on www.fbil.org.in. and www.oanda.com/bvi-en/ Notes:..."
- **Type**: `LOCATION` | **Text**: `"the Supa Facility"` | **Location**: body / paragraph=148
  *Context*: "Any delays or cost overruns in the completion of the construction of the Supa Facility;..."

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
- **Type**: `LOCATION` | **Text**: `"Pune"` | **Location**: table / table=0 / row=1 / cell=0 / paragraph=0
  *Context*: "11/3, 11/4 and 11/5 Village Birdewadi Chakan Taluka - Khed Pune   410 501..."
