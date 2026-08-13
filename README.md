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

The current implementation supports:

- `PERSON` — personal names
- `COMPANY` — organizations and corporate entities
- `LOCATION` — geographical locations and facilities
- `EMAIL` — email addresses
- `PHONE` — telephone and fax numbers
- `SSN` — Social Security / tax identification numbers
- `CREDIT_CARD` — credit and debit card numbers
- `IP_ADDRESS` — IPv4 and IPv6 addresses
- `DATE_OF_BIRTH` — dates identified using contextual validation

Physical or mailing addresses are not listed as a separate detector unless they are identified by one of the supported contextual entity detectors.

## Tradeoffs

The hybrid approach improves coverage compared with using only regex or only NER. Regex patterns are more reliable for structured identifiers, while NER-based detection can identify names and organizations that do not follow a fixed format.

The main tradeoff is precision versus recall. Contextual NER can occasionally classify capitalized business terminology as a person, company, or location. The pipeline therefore applies validation and suppression rules before redaction.

The benchmark also contains overlapping ground-truth annotations. The redaction pipeline resolves these by selecting the longest authoritative span, which can reduce strict exact-span recall even when the sensitive information itself has been covered.

## Evaluation

On the human-annotated benchmark:

| Metric | Strict Exact-Span | Normalized Semantic |
|---|---:|---:|
| Precision | 89.7% | 89.7% |
| Recall | 83.9% | 100.0% |
| F1 | 86.7% | 94.5% |

Standard accuracy is not reported because this is a span-extraction task and a meaningful true-negative population is not defined. The evaluation report explains this limitation and provides the precision, recall, and F1 results.

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
