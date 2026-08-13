# Ground-Truth Evaluation & Metrics Report

This report presents strict exact-span/exact-type metrics calculated against the human-labeled ground truth dataset in `evaluation/ground_truth.json`.

---

## 1. Overall Performance Metrics

| Metric Mode | Precision | Recall | F1-Score | True Positives | False Positives | False Negatives |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Micro Average** | 47.1% | 77.4% | 58.5% | 24 | 27 | 7 |
| **Macro Average** | 62.1% | 80.9% | 68.7% | - | - | - |

---

## 2. Category-Specific Metrics

| PII Category | TP | FP | FN | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `COMPANY` | 11 | 17 | 5 | 39.3% | 68.8% | 50.0% |
| `EMAIL` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `LOCATION` | 6 | 7 | 1 | 46.2% | 85.7% | 60.0% |
| `PERSON` | 1 | 3 | 1 | 25.0% | 50.0% | 33.3% |
| `PHONE` | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% |

---

## 3. Detailed Error Analysis

### Suspected False Positives (Detected but not in Ground Truth)
Total: 27

- **Type**: `COMPANY` | **Text**: `"the General Information Document"` | **Location**: body / paragraph=47
  *Context*: "This Red Herring Prospectus uses certain definitions and abbreviations which, unless the context oth..."
- **Type**: `PERSON` | **Text**: `"Email"` | **Location**: body / paragraph=756
  *Context*: "Telephone: +91 22 40094400 Email: ksh.ipo@nuvama.com Website: www.nuvama.com..."
- **Type**: `PERSON` | **Text**: `"Sarthak Malvadkar Company"` | **Location**: table / table=0 / row=1 / cell=2 / paragraph=1
  *Context*: "Sarthak Malvadkar Company Secretary and Compliance Officer..."
- **Type**: `LOCATION` | **Text**: `"U.S"` | **Location**: body / paragraph=122
  *Context*: "“U.S $”, “U.S. Dollar”, “USD” are to United States Dollars, the official currency of the United Stat..."
- **Type**: `LOCATION` | **Text**: `"U.S."` | **Location**: body / paragraph=122
  *Context*: "“U.S $”, “U.S. Dollar”, “USD” are to United States Dollars, the official currency of the United Stat..."
- **Type**: `LOCATION` | **Text**: `"USD"` | **Location**: body / paragraph=122
  *Context*: "“U.S $”, “U.S. Dollar”, “USD” are to United States Dollars, the official currency of the United Stat..."
- **Type**: `LOCATION` | **Text**: `"United States Dollars"` | **Location**: body / paragraph=122
  *Context*: "“U.S $”, “U.S. Dollar”, “USD” are to United States Dollars, the official currency of the United Stat..."
- **Type**: `LOCATION` | **Text**: `"the United States of America"` | **Location**: body / paragraph=122
  *Context*: "“U.S $”, “U.S. Dollar”, “USD” are to United States Dollars, the official currency of the United Stat..."
- **Type**: `COMPANY` | **Text**: `"the European Union"` | **Location**: body / paragraph=123
  *Context*: "‘EUR’, ‘Euro’ and ‘€’ are to the official currency of the European Union; and..."
- **Type**: `COMPANY` | **Text**: `"SEK"` | **Location**: body / paragraph=124
  *Context*: "“SEK” are to Swedish Krona, the official currency of Sweden...."

---

### Suspected False Negatives (PII Missed by Pipeline)
Total: 7

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
- **Type**: `LOCATION` | **Text**: `"Pune"` | **Location**: table / table=0 / row=1 / cell=0 / paragraph=0
  *Context*: "11/3, 11/4 and 11/5 Village Birdewadi Chakan Taluka - Khed Pune – 410 501..."
- **Type**: `PERSON` | **Text**: `"Sarthak Malvadkar"` | **Location**: table / table=0 / row=1 / cell=2 / paragraph=1
  *Context*: "Sarthak Malvadkar Company Secretary and Compliance Officer..."
