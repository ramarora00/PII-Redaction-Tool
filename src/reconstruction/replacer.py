from typing import List, Any
from docx.text.run import Run
from src.detection.models import PIIEntity
from src.mapping.models import MappedPIISpan
from src.mapping.span_mapper import map_span_to_runs
from src.anonymization.entity_store import EntityStore

def get_paragraph_runs(paragraph: Any) -> List[Run]:
    """
    Crawls the paragraph XML elements to find all runs (w:r), including those
    nested inside hyperlinks (w:hyperlink). Wraps them as python-docx Run objects
    to preserve their formatting.
    """
    runs: List[Run] = []
    # paragraph._p is the underlying lxml element for the paragraph
    for child in paragraph._p:
        # Check namespace-agnostic tags using local-name
        tag_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        
        if tag_name == "r":
            runs.append(Run(child, paragraph))
        elif tag_name == "hyperlink":
            for subchild in child:
                sub_tag = subchild.tag.split("}")[-1] if "}" in subchild.tag else subchild.tag
                if sub_tag == "r":
                    runs.append(Run(subchild, paragraph))
    return runs

def apply_replacements(
    paragraph: Any,
    mapped_spans: List[MappedPIISpan],
    runs: List[Run],
    store: EntityStore
) -> None:
    """
    Applies synthetic replacements to runs inline without destroying surrounding formats.
    Matches are processed right-to-left (descending start offset) to prevent offset drift.
    """
    if not mapped_spans:
        return

    # Sort mapped spans right-to-left by start offset descending
    mapped_spans.sort(key=lambda x: x.entity.start, reverse=True)

    for mapped in mapped_spans:
        entity = mapped.entity
        run_spans = mapped.run_spans
        
        # Resolve synthetic value
        replacement = store.get_replacement(entity.entity_type, entity.text)
        
        # Sort run spans by run index ascending to apply replacements orderly
        run_spans.sort(key=lambda x: x.run_index)
        
        # 1. Apply replacement to the first run in the span
        first_span = run_spans[0]
        first_run = runs[first_span.run_index]
        orig_text_1 = first_run.text if first_run.text is not None else ""
        
        # Slice original run text
        prefix = orig_text_1[:first_span.start_in_run]
        # Suffix is preserved only if this is a single run match
        suffix = orig_text_1[first_span.end_in_run:] if len(run_spans) == 1 else ""
        
        first_run.text = prefix + replacement + suffix
        
        # 2. For all subsequent runs in the span, remove their matched text segments
        for extra_span in run_spans[1:]:
            extra_run = runs[extra_span.run_index]
            orig_text_extra = extra_run.text if extra_run.text is not None else ""
            
            # Suffix is preserved on the last run if there are multiple runs
            sfx = orig_text_extra[extra_span.end_in_run:] if extra_span == run_spans[-1] else ""
            pfx = orig_text_extra[:extra_span.start_in_run]
            
            extra_run.text = pfx + sfx
