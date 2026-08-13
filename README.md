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

## Detection Fusion & Conflict Resolution

In Milestone 3, we implemented the detection fusion and conflict resolution layer:

- **Type Normalization**: Maps detector-specific types to standard canonical types (e.g. `PERSON_CANDIDATE` -> `PERSON`).
- **Duplicate Merging with Provenance**: Candidates covering the exact same span and compatible types are merged. The highest confidence is retained, and original detector signatures (detector name, original score, and original label) are saved under `metadata["sources"]`.
- **Hierarchical Conflict Policy**: Overlapping and nested spans are resolved deterministically:
  1. *Contextual Override*: Specific context-based types (like `DATE_OF_BIRTH`) override generic ones (like `DATE`).
  2. *Nesting Check*:
     - If types are compatible, the larger span wins to preserve complete entities (e.g. `"Mr. John Smith"` over `"John"`).
     - If types are incompatible, the semantically stronger type wins even if nested (e.g., `"john@example.com"` `EMAIL` overrides nested `"john"` `PERSON`).
  3. *Type Strength*: High-strength validated structured types (`EMAIL`, `SSN`, `CREDIT_CARD`, `IP_ADDRESS`) override weaker contextual boundaries if they overlap.
  4. *Confidence & Length*: Fallbacks resolve in favor of higher confidence, then longer span length, then deterministic index positions.
- **Safety Invariants**: The fusion layer asserts `0 <= start < end <= len(text)` and verifies that `text[start:end] == entity.text` matching string values.

## Span Mapping into DOCX Runs

In Milestone 4, we built the span mapping layer:

- **Paragraph-Local Coordinates**: Avoids document-wide index drifting by keeping all text extraction and coordinate mappings strictly localized to individual paragraphs.
- **Unambiguous Container Paths**: Defines `DocumentLocation` supporting container-path generation (e.g. `table / table=2 / row=3 / cell=4 / paragraph=10` or `body / paragraph=10`) to uniquely identify every paragraph in the document structure.
- **Run Intersect Coordinate Mapping**: Slices logical character offsets back to individual DOCX runs, supporting single-run hits, matches split across multiple adjacent runs, and partial-run (mid-run) offsets.
- **Defensive Safety Invariants**: Asserts that the concatenated text of mapped runs matches the PIIEntity text exactly, failing loudly to prevent document payload corruption.

## Anonymization & Entity Resolution

In Milestone 5, we implemented the entity resolution, relationship modeling, and deterministic synthetic identity generation layer:

- **Decoupled Normalization & Resolution**: Decouples comparative string cleanups (stripping titles, trimming spacing, case-insensitivity) from the entity resolution layer (determining if two mentions represent the same underlying entity).
- **Conservative Alias Merging**: Automatically groups exact name overlaps. Resolves short names (e.g. `"Rajesh"`) to full name canonical records (e.g. `"Rajesh Hegde"`) *only* if a single, unique candidate exists in the document, splitting them otherwise to prevent false merges.
- **Typed Keys**: Implements prefix keys (e.g. `PERSON::` and `EMAIL::`) in the store to eliminate cross-type namespace collisions.
- **Stable Seeded Generation**: Derives configuration seeds from the resolved canonical ID (e.g. `PERSON_001`) rather than the raw mention string. This ensures aliases produce identical replacements (e.g. both `"Mr. Rajesh Hegde"` and `"Rajesh Hegde"` map to `"John Smith"`).
- **Format-Preserving Synthetic Values**:
  - *Email*: Replaces email prefixes using a slugified version of the linked fake name.
  - *Credit Card*: Generates random digits passing Luhn validation matching the exact length of the original card, without preserving issuer BIN prefixes.
  - *Phones/SSNs/IPs/Dates*: Replaces digits while keeping the spacing, punctuation, and structural layouts intact.
- **Relationship Preservation**: Links associated emails, phones, and DOB values to `PERSON` canonical profiles, maintaining realistic identity links.

## DOCX Reconstruction & Redaction

In Milestone 6, we implemented the document reconstruction and inline run redaction pipeline:

- **Hyperlink XML Crawler**: Traverses paragraph XML structures to extract child `w:r` elements nested within `w:hyperlink` tags, matching standard runs. This ensures that hyperlinked PII (e.g. email links) is fully redacted.
- **Two-Pass Traverse Parsing**:
  - *Pass 1*: Iterates through body paragraphs, tables (row-by-row, cell-by-cell), section headers, and section footers, detects candidate entities, and registers them globally in the `EntityStore` to resolve aliases.
  - *Pass 2*: Traverses the document again, maps resolved character coordinates back to physical runs, and executes the inline replacement.
- **Right-to-Left Inline Replacement**: Applies replacements sorted by start index descending. Modifying a run's text length inline does not invalidate the offsets of any matches to its left.
- **Unified Inline Replacement Algorithm**:
  - The first run span in a match receives the synthetic replacement text (pre-calculated deterministically).
  - All subsequent run spans have their matched segments deleted while keeping styling and markup structures intact.
- **Atomic Writing**: Saves the output to a temp file, validates it compiles, and moves it to the target output path, leaving the original input document byte-for-byte untouched.






