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

