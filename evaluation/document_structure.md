# Red Herring Prospectus Document Structure Report

**Target Document**: `prospectus.docx`  
**File Size**: 1844676 bytes  

## 📊 Structural Statistics

| Element Type | Count |
| :--- | :--- |
| Primary Paragraphs | 1006 |
| Primary Paragraph Runs | 27457 |
| Tables | 76 |
| Table Rows | 878 |
| Table Cells | 3722 |
| Paragraphs in Cells | 4199 |
| Runs in Cells | 41342 |
| Header Paragraphs | 85 |
| Header Runs | 170 |
| Footer Paragraphs | 85 |
| Footer Runs | 85 |

## 🔍 Run Fragmentation Analysis

In DOCX documents, words or specific phrases (like names, phone numbers, or emails) can be split across multiple consecutive runs due to formatting changes, editing history, or spellcheck markers. Below are sample occurrences where word characters are split:

### Fragment 1
- **Location**: Paragraph Index 46, Run Index 0
- **First Run Text**: `'D'`
- **Second Run Text**: `'EFINITIONS'`
- **Reconstructed word/boundary**: `DEFINITIONS`
- **Visual context**: `...D | EFINITIONS...`

### Fragment 2
- **Location**: Paragraph Index 97, Run Index 0
- **First Run Text**: `'C'`
- **Second Run Text**: `'ERTAIN'`
- **Reconstructed word/boundary**: `CERTAIN`
- **Visual context**: `...C | ERTAIN...`

### Fragment 3
- **Location**: Paragraph Index 137, Run Index 0
- **First Run Text**: `'F'`
- **Second Run Text**: `'ORWARD-LOOKING'`
- **Reconstructed word/boundary**: `FORWARD-LOOKING`
- **Visual context**: `...F | ORWARD-LOOKING...`

### Fragment 4
- **Location**: Paragraph Index 155, Run Index 0
- **First Run Text**: `'S'`
- **Second Run Text**: `'UMMARY'`
- **Reconstructed word/boundary**: `SUMMARY`
- **Visual context**: `...S | UMMARY...`

## 📍 Potential PII Locations and Structural Distribution

To design an effective detection engine, we must know where sensitive information occurs. The following locations contain corporate/legal vocabulary indicating PII containers (e.g. 'director', 'registered office', 'email'):

- **paragraph[6]** (Contains keyword 'pan', length=49 chars)
- **paragraph[16]** (Contains keyword 'pan', length=162 chars)
- **paragraph[20]** (Contains keyword 'pan', length=73 chars)
- **paragraph[24]** (Contains keyword 'director', length=1847 chars)
- **paragraph[26]** (Contains keyword 'registered office', length=116 chars)
- **paragraph[28]** (Contains keyword 'phone', length=106 chars)
- **paragraph[31]** (Contains keyword 'pan', length=162 chars)
- **paragraph[48]** (Contains keyword 'registered office', length=487 chars)
- **paragraph[49]** (Contains keyword 'pan', length=279 chars)
- **paragraph[55]** (Contains keyword 'pan', length=21 chars)
- **table[0].row[0].cell[0].paragraph[0]** (Table cell contains keyword 'registered office', length=17 chars)
- **table[0].row[0].cell[4].paragraph[0]** (Table cell contains keyword 'phone', length=20 chars)
- **table[0].row[0].cell[5].paragraph[0]** (Table cell contains keyword 'phone', length=20 chars)
- **table[0].row[1].cell[2].paragraph[1]** (Table cell contains keyword 'pan', length=58 chars)
- **table[0].row[1].cell[3].paragraph[1]** (Table cell contains keyword 'pan', length=58 chars)
- **table[0].row[1].cell[4].paragraph[1]** (Table cell contains keyword 'email', length=66 chars)
- **table[0].row[1].cell[5].paragraph[1]** (Table cell contains keyword 'email', length=66 chars)
- **table[0].row[2].cell[0].paragraph[0]** (Table cell contains keyword 'promoter', length=262 chars)
- **table[0].row[2].cell[1].paragraph[0]** (Table cell contains keyword 'promoter', length=262 chars)
- **table[0].row[2].cell[2].paragraph[0]** (Table cell contains keyword 'promoter', length=262 chars)

## 💡 Key Engineering Observations & Implications

### 1. Run-level Fragmentation
- **Observation**: Text is indeed split across runs. If we try to perform regex matching run-by-run, many entities (such as names, addresses, or phone numbers) will be missed.
- **Design Decision**: Detection must be performed at the **paragraph** level (by consolidating run texts) rather than individual runs. We must then map detected character spans back to the corresponding runs.

### 2. High Density of Tables
- **Observation**: A significant amount of key structured information (e.g., names of Whole-time Directors, registered addresses, bank details, phone numbers) is located in tables.
- **Design Decision**: The pipeline must recursively inspect all cells inside all tables and treat cell paragraphs identically to document paragraphs.

### 3. Headers and Footers
- **Observation**: Headers and footers exist in the document and contain metadata. While less likely to contain personal director details, they can contain corporate identifiers or contact info.
- **Design Decision**: The engine must inspect and replace PII in headers and footers to ensure completeness.

### 4. Preservation of Formatting
- **Observation**: Runs contain distinct styles (bold, font size, hyperlinks). Replacing text inside runs can break styling if we do not reconstruct the runs carefully.
- **Design Decision**: The replacement phase should rebuild run texts while preserving their format templates, or split/merge runs correctly to accommodate the new replacement string size.
