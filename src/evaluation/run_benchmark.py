import os
import json
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
from docx import Document

from src.detection.regex_detector import RegexDetector
from src.detection.ner_detector import NERDetector
from src.detection.presidio_detector import PresidioDetector
from src.detection.fusion import resolve_candidates
from src.detection.validation import CandidateValidator
from src.mapping.span_mapper import reconstruct_paragraph_text
from src.reconstruction.replacer import get_paragraph_runs

def find_block(doc: Document, path: str) -> Any:
    """
    Parses a unique container path and retrieves the corresponding paragraph element.
    """
    parts = [p.strip() for p in path.split("/")]
    container_type = parts[0]
    
    try:
        if container_type == "body":
            p_idx = int(parts[1].split("=")[1])
            return doc.paragraphs[p_idx]
        elif container_type == "table":
            t_idx = int(parts[1].split("=")[1])
            r_idx = int(parts[2].split("=")[1])
            c_idx = int(parts[3].split("=")[1])
            p_idx = int(parts[4].split("=")[1])
            return doc.tables[t_idx].rows[r_idx].cells[c_idx].paragraphs[p_idx]
        elif container_type == "header":
            s_idx = int(parts[1].split("=")[1])
            p_idx = int(parts[2].split("=")[1])
            return doc.sections[s_idx].header.paragraphs[p_idx]
        elif container_type == "footer":
            s_idx = int(parts[1].split("=")[1])
            p_idx = int(parts[2].split("=")[1])
            return doc.sections[s_idx].footer.paragraphs[p_idx]
    except Exception as e:
        print(f"Error parsing path {path}: {e}")
    return None

def compute_metrics(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    """
    Calculates Precision, Recall, and F1.
    """
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1

def run_benchmark_eval(gt_path: str, doc_path: str, report_output_path: str) -> None:
    if not os.path.exists(gt_path):
        raise FileNotFoundError(f"Ground truth file not found at: {gt_path}")
    if not os.path.exists(doc_path):
        raise FileNotFoundError(f"Prospectus file not found at: {doc_path}")

    # Load Ground Truth
    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    doc = Document(doc_path)

    # Instantiate Pipeline
    regex_detector = RegexDetector()
    ner_detector = NERDetector()
    presidio_detector = PresidioDetector()
    candidate_validator = CandidateValidator()

    # Track TP, FP, FN per category
    metrics_per_category: Dict[str, Dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    
    # Track overall counts
    total_tp = 0
    total_fp = 0
    total_fn = 0

    # Detailed list of failures for error analysis
    false_positives_list: List[Dict[str, Any]] = []
    false_negatives_list: List[Dict[str, Any]] = []

    print(f"Evaluating {len(gt_data['blocks'])} blocks against human ground truth...")

    for block_entry in gt_data["blocks"]:
        path = block_entry["container_path"]
        gt_entities = block_entry["entities"]
        
        paragraph = find_block(doc, path)
        if not paragraph:
            print(f"Warning: Could not find block for path: {path}")
            continue

        # Run pipeline
        runs = get_paragraph_runs(paragraph)
        if not runs:
            # If ground truth expected entities but block has no runs, treat all as FN
            for gt in gt_entities:
                metrics_per_category[gt["entity_type"]]["fn"] += 1
                total_fn += 1
            continue

        text, offsets = reconstruct_paragraph_text(runs)
        
        # 1. Detect
        cands = (
            regex_detector.detect(text) +
            ner_detector.detect(text) +
            presidio_detector.detect(text)
        )
        
        # 2. Fuse
        resolved = resolve_candidates(text, cands)
        resolved_pii = [e for e in resolved if e.entity_type != "DATE"]

        # 3. Validate
        validated = candidate_validator.validate_candidates(text, resolved_pii)
        pred_entities = [e for e in validated if e.metadata.get("validation_decision") == "KEEP"]

        # Exact matching logic (start, end, entity_type)
        matched_gt_indices = set()
        
        for pred in pred_entities:
            # Search for exact match in ground truth
            found_match = False
            for idx, gt in enumerate(gt_entities):
                if idx in matched_gt_indices:
                    continue
                # Match start, end, type exactly
                if (gt["start"] == pred.start and 
                    gt["end"] == pred.end and 
                    gt["entity_type"] == pred.entity_type):
                    
                    metrics_per_category[pred.entity_type]["tp"] += 1
                    total_tp += 1
                    matched_gt_indices.add(idx)
                    found_match = True
                    break
                    
            if not found_match:
                metrics_per_category[pred.entity_type]["fp"] += 1
                total_fp += 1
                false_positives_list.append({
                    "path": path,
                    "text": pred.text,
                    "type": pred.entity_type,
                    "context": text
                })

        # Any remaining unmatched gt items are False Negatives
        for idx, gt in enumerate(gt_entities):
            if idx not in matched_gt_indices:
                metrics_per_category[gt["entity_type"]]["fn"] += 1
                total_fn += 1
                false_negatives_list.append({
                    "path": path,
                    "text": gt["text"],
                    "type": gt["entity_type"],
                    "context": text
                })

    # Compute category summaries
    all_categories = sorted(list(set(list(metrics_per_category.keys()) + ["PERSON", "COMPANY", "LOCATION", "EMAIL", "PHONE"])))
    category_summary_rows = []
    
    macro_precision_sum = 0.0
    macro_recall_sum = 0.0
    macro_f1_sum = 0.0
    active_categories = 0

    for cat in all_categories:
        counts = metrics_per_category[cat]
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        p, r, f1 = compute_metrics(tp, fp, fn)
        
        category_summary_rows.append(
            f"| `{cat}` | {tp} | {fp} | {fn} | {p*100:.1f}% | {r*100:.1f}% | {f1*100:.1f}% |"
        )
        
        # Macro averages are computed over categories that have at least one representation in TP/FP/FN
        if (tp + fp + fn) > 0:
            macro_precision_sum += p
            macro_recall_sum += r
            macro_f1_sum += f1
            active_categories += 1

    # Overall Micro metrics
    micro_precision, micro_recall, micro_f1 = compute_metrics(total_tp, total_fp, total_fn)
    
    # Overall Macro metrics
    if active_categories > 0:
        macro_precision = macro_precision_sum / active_categories
        macro_recall = macro_recall_sum / active_categories
        macro_f1 = macro_f1_sum / active_categories
    else:
        macro_precision, macro_recall, macro_f1 = 0.0, 0.0, 0.0

    # Write Metrics Report
    os.makedirs(os.path.dirname(os.path.abspath(report_output_path)), exist_ok=True)
    
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(f"""# Ground-Truth Evaluation & Metrics Report

This report presents strict exact-span/exact-type metrics calculated against the human-labeled ground truth dataset in `evaluation/ground_truth.json`.

---

## 1. Overall Performance Metrics

| Metric Mode | Precision | Recall | F1-Score | True Positives | False Positives | False Negatives |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Micro Average** | {micro_precision*100:.1f}% | {micro_recall*100:.1f}% | {micro_f1*100:.1f}% | {total_tp} | {total_fp} | {total_fn} |
| **Macro Average** | {macro_precision*100:.1f}% | {macro_recall*100:.1f}% | {macro_f1*100:.1f}% | - | - | - |

---

## 2. Category-Specific Metrics

| PII Category | TP | FP | FN | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
""" + "\n".join(category_summary_rows) + f"""

---

## 3. Detailed Error Analysis

### Suspected False Positives (Detected but not in Ground Truth)
Total: {len(false_positives_list)}

""" + "\n".join([f"- **Type**: `{fp['type']}` | **Text**: `\"{fp['text']}\"` | **Location**: {fp['path']}\n  *Context*: \"{fp['context'].strip()[:100]}...\"" for fp in false_positives_list[:10]]) + f"""

---

### Suspected False Negatives (PII Missed by Pipeline)
Total: {len(false_negatives_list)}

""" + "\n".join([f"- **Type**: `{fn['type']}` | **Text**: `\"{fn['text']}\"` | **Location**: {fn['path']}\n  *Context*: \"{fn['context'].strip()[:100]}...\"" for fn in false_negatives_list[:10]]) + """
""")
    print(f"Benchmark metrics report successfully generated at: {report_output_path}")

if __name__ == "__main__":
    run_benchmark_eval("evaluation/ground_truth.json", "data/input/prospectus.docx", "evaluation/evaluation_metrics.md")
