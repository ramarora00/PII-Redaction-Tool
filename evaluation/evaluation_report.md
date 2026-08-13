# PII Redaction Tool — Evaluation Report

## 1. Objective

The purpose of this evaluation is to measure how accurately the PII redaction pipeline identifies sensitive entities in the supplied prospectus and to verify that the resulting DOCX remains structurally intact.

The evaluation focuses on:

1. Precision — whether detected spans correspond to actual PII.
2. Recall — whether annotated PII is detected.
3. F1-score — the balance between precision and recall.
4. Structural preservation — whether redaction changes the document structure.
5. Residual PII checks — whether original critical values remain in the output.

---

## 2. Evaluation Dataset

The evaluation uses:

```text
data/input/prospectus.docx
```

A benchmark containing 50 annotated text blocks was created from the prospectus and stored in:

```text
evaluation/ground_truth.json
```

The ground truth contains annotations for:

* `COMPANY`
* `LOCATION`
* `PERSON`
* `EMAIL`
* `PHONE`
* `ADDRESS`

The benchmark was used to compare the spans detected by the pipeline against human-annotated PII.

---

## 3. Evaluation Method

Two matching protocols were used.

### 3.1 Strict Exact-Span Matching

A prediction is counted as a true positive only when:

* the predicted start offset matches the ground-truth start offset,
* the predicted end offset matches the ground-truth end offset, and
* the predicted entity type matches the ground-truth type.

Boundary or classification differences therefore affect both precision and recall.

### 3.2 Project-Specific Normalized Semantic Matching

The prospectus contains cases where annotations overlap.

For example, the ground truth contains both:

```text
Registrar of Companies
Registrar of Companies, Maharashtra
```

The pipeline resolves overlapping candidates by retaining the longer authoritative span.

Strict matching treats the shorter annotation as missed even though the larger replacement covers the same sensitive information. This project-specific evaluation protocol removes this overlap effect by evaluating the authoritative entity coverage instead. It is a custom protocol designed for the supplied overlapping ground truth and should not be interpreted as a standardized benchmark metric.

---

## 4. Metrics

The standard definitions used are:

### Precision

```text
Precision = TP / (TP + FP)
```

Precision measures the proportion of predicted redactions that correspond to ground-truth PII.

### Recall

```text
Recall = TP / (TP + FN)
```

Recall measures the proportion of ground-truth PII spans covered by the system.

### F1-score

```text
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

F1 combines precision and recall into a single measure.

### Accuracy

The assignment requests an explicit accuracy metric. Because conventional span-level accuracy is not well-defined for this span-based evaluation, Accuracy is calculated via explicit **Token-Level Binary Classification** over all evaluated benchmark blocks.

For every token in the benchmark text (using whitespace tokenization), the token is classified as either PII or NON-PII for both the ground truth and the prediction. Overlapping ground-truth annotations are deduplicated prior to labeling.

The metric is calculated as:
* **TP:** actual PII predicted as PII
* **TN:** actual non-PII predicted as non-PII
* **FP:** actual non-PII predicted as PII
* **FN:** actual PII predicted as non-PII

Accuracy = `(TP + TN) / (TP + TN + FP + FN)`

---

## 5. Overall Results

The implementation supports all 9 Enterprise-required PII categories. The supplied prospectus benchmark contains annotations for COMPANY, LOCATION, PERSON, EMAIL, PHONE, and ADDRESS. SSN, CREDIT_CARD, DATE_OF_BIRTH, and IP_ADDRESS do not occur in the supplied prospectus, so no category-level benchmark scores are reported for those types.

### Token-Level Binary Classification

| Metric | Accuracy | TP | TN | FP | FN |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Overall | 99.0% | 86 | 929 | 10 | 0 |

### Span Matching Metrics

| Evaluation Protocol | Precision | Recall | F1-score | TP | FP | FN |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Strict Exact-Span | 87.5% |  82.4% |    84.8% | 28 |  4 |  6 |
| Project-Specific Normalized Semantic | 90.6% | 100.0% | 95.1% | 29 |  3 |  0 |

### Summary

**Primary evaluation**

* Token-level accuracy: **99.0%**
* Strict precision: **87.5%**
* Strict recall: **82.4%**
* Strict F1-score: **84.8%**

**Additional diagnostic evaluation**

* Normalized semantic precision: **90.6%**
* Normalized semantic recall: **100.0%**
* Normalized semantic F1-score: **95.1%**

The normalized semantic evaluation is included as an additional diagnostic analysis to account for overlapping annotations in the manually created benchmark. The primary reported evaluation remains the strict span-based evaluation.

---

## 6. Category-Level Results

### Strict Exact-Span

| Category | TP | FP | FN | Precision | Recall |     F1 |
| -------- | -: | -: | -: | --------: | -----: | -----: |
| ADDRESS  |  2 |  1 |  1 |     66.7% |  66.7% |  66.7% |
| COMPANY  | 11 |  1 |  5 |     91.7% |  68.8% |  78.6% |
| EMAIL    |  3 |  0 |  0 |    100.0% | 100.0% | 100.0% |
| LOCATION |  7 |  1 |  0 |     87.5% | 100.0% |  93.3% |
| PERSON   |  2 |  1 |  0 |     66.7% | 100.0% |  80.0% |
| PHONE    |  3 |  0 |  0 |    100.0% | 100.0% | 100.0% |

### Project-Specific Normalized Semantic

| Category | TP | FP | FN | Precision | Recall |     F1 |
| -------- | -: | -: | -: | --------: | -----: | -----: |
| ADDRESS  |  3 |  0 |  0 |    100.0% | 100.0% | 100.0% |
| COMPANY  | 11 |  1 |  0 |     91.7% | 100.0% |  95.7% |
| EMAIL    |  3 |  0 |  0 |    100.0% | 100.0% | 100.0% |
| LOCATION |  7 |  1 |  0 |     87.5% | 100.0% |  93.3% |
| PERSON   |  2 |  1 |  0 |     66.7% | 100.0% |  80.0% |
| PHONE    |  3 |  0 |  0 |    100.0% | 100.0% | 100.0% |

---

## 7. False Positives

Four false positives were identified during benchmark evaluation.

### 7.1 Company

```text
the General Information Document
```

This phrase was classified as a company because its capitalization and wording resembled an organization name.

### 7.2 Person

```text
Reference Rate
```

This financial term was classified as a person name by the contextual NER component.

### 7.3 Location

```text
the Supa Facility
```

The phrase was classified as a location because of its facility-related context.

### 7.4 Address

```text
3 Inspire BKC G Block, Bandra Kurla Complex
```

The strict evaluator counted this as a false positive because the exact predicted span boundaries for the address component slightly deviated from the annotation boundaries. Under overlapping semantic evaluation, this resolves to a true positive.

These examples illustrate the main precision limitation of contextual logic: ordinary terminology can resemble named entities, and boundaries may vary slightly from human annotations.

---

## 8. False Negatives

The six strict false negatives occur around:

```text
Registrar of Companies
Registrar of Companies, Maharashtra
```

The ground truth contains overlapping annotations for these spans.

The pipeline resolves the overlap by selecting the longer authoritative entity:

```text
Registrar of Companies, Maharashtra
```

Consequently, the shorter annotation is counted as a false negative by the strict evaluator even though the larger sensitive span is redacted. A similar boundary mismatch affects an `ADDRESS` span.

After normalization of the overlapping and slightly offset annotations, the false-negative count becomes zero and recall becomes 100.0% on the evaluated benchmark under the project-specific normalized semantic protocol.

---

## 9. Precision / Recall Tradeoff

The system uses different detection strategies for different PII types.

Regex-based detection is used where the data has a recognizable structure, such as:

* email addresses
* phone numbers
* SSNs
* credit card numbers
* IP addresses

These detectors provide relatively precise boundaries.

NER-based detection is useful for entities such as:

* person names
* organizations
* locations

but is more dependent on surrounding context.

The system therefore combines the detectors and applies candidate fusion and validation before reconstruction.

A further tradeoff exists in global propagation. Multi-word person names and sufficiently specific company names can be propagated to repeated occurrences. Single-word names and generic locations are not automatically propagated because doing so could cause unrelated uses of common words or place names to be redacted.

---

## 10. Structural Assurance

The final output was checked against the original document.

The following counts were unchanged:

| Component         | Count | Result |
| ----------------- | ----: | ------ |
| Body paragraphs   | 1,006 | Passed |
| Tables            |    76 | Passed |
| Table cells       | 3,722 | Passed |
| Sections          |    85 | Passed |
| Header paragraphs |    85 | Passed |
| Footer paragraphs |    85 | Passed |

The reconstruction tests also verify handling of text distributed across DOCX runs.

---

## 11. Residual PII Checks

Two additional assurance checks were performed on the final redacted document.

### Tier 1 — Critical PII Search

The output was searched for 178 unique critical PII values, including names, email addresses, phone numbers, SSNs, and credit-card values.

Result:

```text
Critical PII leaks: 0
```

### Tier 2 — Source Span Verification

The generated replacements were checked against their original source locations.

Result:

```text
Redaction spans checked: 1,953
Verification failures: 0
```

---

## 12. Automated Tests

The final implementation was tested using the project's unit and integration test suite.

```text
Tests executed: 77
Tests passed:   77
Tests failed:   0
```

The tests cover detection, candidate propagation, span mapping, reconstruction, and redaction assurance behavior.

---

## 13. Limitations

The evaluation should be interpreted within the scope of the supplied prospectus and benchmark.

1. Single-word names and generic locations are not globally propagated because aggressive propagation could increase false positives.
2. Contextual NER can classify capitalized business terminology as a person, company, or location.
3. Strict span evaluation penalizes the system when ground-truth annotations overlap.
4. Complex DOCX formatting where text is separated by non-contiguous XML structures can make span reconstruction more difficult.
5. The benchmark does not establish performance on every possible document type or every possible form of PII.

---

## 14. Conclusion

The evaluated pipeline achieved:

* **99.0% token-level accuracy**
* **87.5% precision**
* **82.4% strict exact-span recall**
* **84.8% strict F1-score**
* **100.0% project-specific normalized semantic recall**
* **95.1% project-specific normalized semantic F1-score**

The final document also passed the structural checks, with all tested document component counts preserved, and the critical PII audit found zero residual values from the checked set.

These results indicate strong detection performance on the categories represented in the supplied human-annotated benchmark, while the implementation additionally supports the other required PII categories. Structural and residual-PII checks provide complementary evidence for the generated document.
