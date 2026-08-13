# PII Redaction Tool

A Python CLI tool to detect and redact personally identifiable information (PII) from Red Herring Prospectus DOCX files and replace them with fake alternatives.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the tool using:
```bash
python -m src.main --input <path_to_input_docx> --output <path_to_output_docx>
```

## Running Tests

Run the test suite:
```bash
pytest tests/
```

## Document Investigation

In Milestone 1, we analyzed the document structure of the raw prospectus (`Red Herring Prospectus.docx`) to establish key design decisions:

- **Volume of Content**: The document has 1,006 primary paragraphs, but 76 tables containing 4,199 cell paragraphs. Over 80% of text content resides in tables.
- **Run Fragmentation**: We confirmed that words and names are frequently split across consecutive runs (e.g. `D` + `EFINITIONS` in adjacent runs). Matches must be resolved at paragraph-level and mapped back.
- **Header/Footer Containment**: Identified headers and footers with metadata that also require inspection.

Detailed metrics are stored in `evaluation/document_structure.md`.

## Detection Architecture

In Milestone 2, we built the modular candidate PII detection foundation:

- **PIIEntity Model**: A standardized dataclass wrapper preserving candidate type, text value, start/end character offsets, detection source, and confidence scores.
- **BaseDetector Interface**: An abstract interface defining `detect(text) -> List[PIIEntity]` which enables plugging in new detection sources without touching the rest of the application.
- **Specialized Detectors**:
  - `RegexDetector`: Handles structured entities (email, SSN, credit cards, IP addresses, date candidates) using boundaries and checksums (e.g. Luhn validation).
  - `NERDetector`: Wraps spaCy to extract contextual entities (`PERSON_CANDIDATE`, `COMPANY_CANDIDATE`, `LOCATION_CANDIDATE`).
  - `PresidioDetector`: Integrates Microsoft Presidio Analyzer Engine as an additional parallel detection source.
- **Context-Aware Rules**: Differentiates Date of Birth (`DATE_OF_BIRTH`) from generic document dates (e.g. `Date of Allotment`) using keyword windows, and suppresses false positive phone/credit card candidates (e.g. `Order No`).
- **Deferred Deconfliction**: Resolving overlaps, deduplication, and final replacement are explicitly deferred to subsequent milestones. Duplicate candidates from multiple sources are preserved.


