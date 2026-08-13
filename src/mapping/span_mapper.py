from typing import List, Tuple, Any
from src.detection.models import PIIEntity
from src.mapping.models import MappedRunSpan, MappedPIISpan

def reconstruct_paragraph_text(runs: List[Any]) -> Tuple[str, List[Tuple[int, int]]]:
    """
    Reconstructs logical text from a list of DOCX Run objects.
    Returns:
      - Reconstructed logical text string
      - List of character offset boundaries (start, end) for each run
    """
    text = ""
    offsets: List[Tuple[int, int]] = []
    for run in runs:
        run_text = run.text if run.text is not None else ""
        # Normalize Unicode dashes / special characters / whitespace to standard spaces for clean token boundaries
        normalized = run_text.replace("\u2013", " ").replace("\u2014", " ").replace("\ufffd", " ").replace("\t", " ").replace("\xa0", " ")
        start_offset = len(text)
        end_offset = start_offset + len(normalized)
        text += normalized
        offsets.append((start_offset, end_offset))
    return text, offsets

def map_span_to_runs(
    span_start: int,
    span_end: int,
    entity: PIIEntity,
    run_offsets: List[Tuple[int, int]],
    runs: List[Any]
) -> List[MappedRunSpan]:
    """
    Maps a logical text character span back to individual runs that contain it.
    Verifies physical boundaries and safety invariants, failing loudly on mismatch.
    """
    if not (0 <= span_start < span_end):
        raise ValueError(f"Invalid span parameters: [{span_start}:{span_end}]")

    run_spans: List[MappedRunSpan] = []
    
    for idx, (r_start, r_end) in enumerate(run_offsets):
        # Calculate overlap between run span [r_start:r_end] and PII span [span_start:span_end]
        overlap_start = max(r_start, span_start)
        overlap_end = min(r_end, span_end)
        
        if overlap_start < overlap_end:
            # Overlap exists
            start_in_run = overlap_start - r_start
            end_in_run = overlap_end - r_start
            
            run_text = runs[idx].text if runs[idx].text is not None else ""
            
            # Boundary check inside run
            if not (0 <= start_in_run <= end_in_run <= len(run_text)):
                raise ValueError(
                    f"Physical boundary failure: run index {idx} offsets [{start_in_run}:{end_in_run}] "
                    f"exceed run text length {len(run_text)}"
                )
                
            text_in_run = run_text[start_in_run:end_in_run]
            
            run_spans.append(MappedRunSpan(
                run_index=idx,
                start_in_run=start_in_run,
                end_in_run=end_in_run,
                text_in_run=text_in_run
            ))

    # Safety Invariant Check: Combined matched text must equal the original PII entity text exactly (modulo normalized whitespace/dashes)
    def normalize_for_check(t: str) -> str:
        return t.replace("\u2013", " ").replace("\u2014", " ").replace("\ufffd", " ").replace("\t", " ").replace("\xa0", " ")

    combined_matched_text = "".join(r.text_in_run for r in run_spans)
    if normalize_for_check(combined_matched_text) != normalize_for_check(entity.text):
        raise ValueError(
            f"Safety Invariant Failed: reconstructed text '{combined_matched_text}' "
            f"does not match PII Entity text '{entity.text}' exactly."
        )

    return run_spans
