# Ground-Truth Evaluation & Metrics Report

This report presents strict exact-span/exact-type metrics calculated against the human-labeled ground truth dataset in `evaluation/ground_truth.json`.

---

## 1. Overall Performance Metrics

| Metric Mode | Precision | Recall | F1-Score | True Positives | False Positives | False Negatives |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Micro Average** | 35.8% | 61.3% | 45.2% | 19 | 34 | 12 |
| **Macro Average** | 57.4% | 73.0% | 62.8% | - | - | - |

---

## 2. Category-Specific Metrics

| PII Category | TP | FP | FN | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `COMPANY` | 7 | 23 | 9 | 23.3% | 43.8% | 30.4% |
| `EMAIL` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `LOCATION` | 5 | 8 | 2 | 38.5% | 71.4% | 50.0% |
| `PERSON` | 1 | 3 | 1 | 25.0% | 50.0% | 33.3% |
| `PHONE` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |

---

## 3. Detailed Error Analysis

### Suspected False Positives (Detected but not in Ground Truth)
Total: 34

- **Type**: `COMPANY` | **Text**: `"Pune"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"the General Information Document"` | **Location**: body / paragraph=47
  *Context*: "This Red Herring Prospectus uses certain definitions and abbreviations which, unless the context oth..."
- **Type**: `PERSON` | **Text**: `"Email"` | **Location**: body / paragraph=756
  *Context*: "Telephone: +91 22 40094400 Email: ksh.ipo@nuvama.com Website: www.nuvama.com..."
- **Type**: `PERSON` | **Text**: `"Sarthak Malvadkar Company"` | **Location**: table / table=0 / row=1 / cell=2 / paragraph=1
  *Context*: "Sarthak Malvadkar Company Secretary and Compliance Officer..."
- **Type**: `COMPANY` | **Text**: `"General Terms and Abbreviations"` | **Location**: body / paragraph=79
  *Context*: "Conventional and General Terms and Abbreviations..."
- **Type**: `COMPANY` | **Text**: `"Key Financial"` | **Location**: body / paragraph=93
  *Context*: "Key Financial and Operating Metrics used in this Red Herring Prospectus..."
- **Type**: `COMPANY` | **Text**: `"CURRENCY"` | **Location**: body / paragraph=97
  *Context*: "CERTAIN CONVENTIONS, USE OF FINANCIAL INFORMATION AND MARKET DATA AND CURRENCY OF PRESENTATION..."
- **Type**: `COMPANY` | **Text**: `"INR"` | **Location**: body / paragraph=121
  *Context*: "“Rupees” or “INR” or “₹” or “Rs.” are to Indian Rupees, the official currency of the Republic of Ind..."
- **Type**: `COMPANY` | **Text**: `"Indian Rupees"` | **Location**: body / paragraph=121
  *Context*: "“Rupees” or “INR” or “₹” or “Rs.” are to Indian Rupees, the official currency of the Republic of Ind..."
- **Type**: `LOCATION` | **Text**: `"the Republic of India"` | **Location**: body / paragraph=121
  *Context*: "“Rupees” or “INR” or “₹” or “Rs.” are to Indian Rupees, the official currency of the Republic of Ind..."

---

### Suspected False Negatives (PII Missed by Pipeline)
Total: 12

- **Type**: `LOCATION` | **Text**: `"Pune"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies, Maharashtra"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies, Maharashtra"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies, Maharashtra"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"Registrar of Companies, Central Processing Centre"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
- **Type**: `COMPANY` | **Text**: `"RoC"` | **Location**: body / paragraph=24
  *Context*: "Our Company was originally incorporated as “Bhandary Metal Extrusion Private Limited” under the prov..."
