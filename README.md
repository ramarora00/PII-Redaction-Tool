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
