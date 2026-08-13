# PII Redaction Tool

A Python command-line tool for detecting and redacting personally identifiable information (PII) from Microsoft Word (`.docx`) documents. The implementation combines regular-expression detectors with spaCy and Microsoft Presidio for structured and contextual PII, then replaces detected values with synthetic alternatives while preserving the document's formatting and structure.

## Approach

The pipeline uses:

- **Regex-based detection** for structured values such as email addresses, phone numbers, SSNs, credit cards, and IP addresses.
- **spaCy / Microsoft Presidio** for contextual entities such as person, company, and location names.
- **Candidate fusion and validation** to resolve overlapping detections and remove common false positives.
- **Entity resolution** to keep synthetic replacements consistent for repeated references.
- **DOCX run-level reconstruction** to replace text without changing the document's paragraph, table, section, header, footer, or formatting structure.

Detected entities are replaced with synthetic values rather than simply removed. The replacement strategy preserves the surrounding document context while preventing the original sensitive values from remaining in the output.

## Supported PII Types

The current implementation supports the following required categories:

- `PERSON` — personal names
- `COMPANY` — organizations and corporate entities
- `ADDRESS` — physical and mailing addresses (such as registered office locations)
- `EMAIL` — email addresses
- `PHONE` — telephone and fax numbers
- `SSN` — Social Security numbers
- `CREDIT_CARD` — credit and debit card numbers
- `IP_ADDRESS` — IPv4 and IPv6 addresses
- `DATE_OF_BIRTH` — dates identified using contextual validation

**Additional supported entity:**
- `LOCATION` — geographical locations and facilities

## Tradeoffs

The hybrid approach improves coverage compared with using only regex or only NER. Regex patterns are more reliable for structured identifiers, while NER-based detection can identify names and organizations that do not follow a fixed format.

The main tradeoff is precision versus recall. Contextual NER can occasionally classify capitalized business terminology as a person, company, or location. The pipeline therefore applies validation and suppression rules before redaction.

## Evaluation

The implementation supports all 9 Enterprise-required PII categories, plus `LOCATION`. The supplied human-annotated benchmark contains verified annotations for `COMPANY`, `LOCATION`, `PERSON`, `EMAIL`, `PHONE`, and `ADDRESS`. However, `SSN`, `CREDIT_CARD`, `DATE_OF_BIRTH`, and `IP_ADDRESS` are explicitly absent from the supplied prospectus document. Therefore, the benchmark metrics directly measure the verified categories only, without fabricating results for absent types.

On the human-annotated benchmark:

### Token-Level Binary Classification

* Accuracy: **99.0%**

### Strict Exact-Span

| Metric | Result |
|---|---:|
| Precision | 87.5% |
| Recall | 82.4% |
| F1-score | 84.8% |

### Project-Specific Normalized Semantic

| Metric | Result |
|---|---:|
| Precision | 90.6% |
| Recall | 100.0% |
| F1-score | 95.1% |

Note: The assignment requests accuracy. To provide a defensible metric, Accuracy is calculated via explicit Token-Level Binary Classification over all benchmark blocks (TP=86, TN=929, FP=10, FN=0). See `evaluation/evaluation_report.md` for the exact calculation methodology.

## Running the Project

Install the dependencies:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Run redaction:

```bash
python -m src.main --input data/input/prospectus.docx --output data/output/prospectus_redacted.docx
```

Run the test suite:

```bash
pytest tests/
```

Run the benchmark:

```bash
python -m src.evaluation.run_benchmark
```

Run the structural and zero-leak assurance checks:

```bash
python -m src.evaluation.redaction_assurance
```

See `evaluation/evaluation_report.md` for the evaluation methodology, detailed results, false-positive/false-negative analysis, and structural assurance results.
