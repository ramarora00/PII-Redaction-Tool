import pytest
from src.detection.models import PIIEntity
from src.mapping.models import DocumentLocation, ParagraphMapping, MappedPIISpan
from src.mapping.span_mapper import reconstruct_paragraph_text, map_span_to_runs

class MockRun:
    def __init__(self, text: str, bold: bool = False, italic: bool = False):
        self.text = text
        self.bold = bold
        self.italic = italic

# ==============================================================================
# SPAN MAPPER UNIT TESTS
# ==============================================================================

def test_reconstruct_paragraph_text():
    runs = [
        MockRun("The Whole-"),
        MockRun("time "),
        MockRun("Director Rajesh Hegde")
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    
    assert text == "The Whole-time Director Rajesh Hegde"
    assert offsets == [
        (0, 10),   # "The Whole-"
        (10, 15),  # "time "
        (15, 36)   # "Director Rajesh Hegde"
    ]

def test_pii_entirely_inside_one_run():
    runs = [
        MockRun("The Director is "),
        MockRun("Rajesh Hegde"),
        MockRun(" (Managing Director).")
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    entity = PIIEntity("PERSON", "Rajesh Hegde", 16, 28, 0.95, "presidio")
    
    mapped_runs = map_span_to_runs(16, 28, entity, offsets, runs)
    
    assert len(mapped_runs) == 1
    assert mapped_runs[0].run_index == 1
    assert mapped_runs[0].start_in_run == 0
    assert mapped_runs[0].end_in_run == 12
    assert mapped_runs[0].text_in_run == "Rajesh Hegde"

def test_cross_run_generic_span():
    # Test "Whole-time" split across runs "Whole-" and "time"
    runs = [
        MockRun("The "),
        MockRun("Whole-"),
        MockRun("time "),
        MockRun("Director")
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    entity = PIIEntity("GENERIC", "Whole-time", 4, 14, 0.90, "regex")
    
    mapped_runs = map_span_to_runs(4, 14, entity, offsets, runs)
    
    assert len(mapped_runs) == 2
    # First run "Whole-"
    assert mapped_runs[0].run_index == 1
    assert mapped_runs[0].start_in_run == 0
    assert mapped_runs[0].end_in_run == 6
    assert mapped_runs[0].text_in_run == "Whole-"
    
    # Second run "time " (matches "time")
    assert mapped_runs[1].run_index == 2
    assert mapped_runs[1].start_in_run == 0
    assert mapped_runs[1].end_in_run == 4
    assert mapped_runs[1].text_in_run == "time"

def test_pii_split_across_many_runs():
    # "Director" split as "Di", "rec", "tor"
    runs = [
        MockRun("The "),
        MockRun("Di"),
        MockRun("rec"),
        MockRun("tor"),
        MockRun(" is Rajesh.")
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    entity = PIIEntity("ROLE", "Director", 4, 12, 0.85, "regex")
    
    mapped_runs = map_span_to_runs(4, 12, entity, offsets, runs)
    
    assert len(mapped_runs) == 3
    assert mapped_runs[0].text_in_run == "Di"
    assert mapped_runs[1].text_in_run == "rec"
    assert mapped_runs[2].text_in_run == "tor"

def test_pii_beginning_mid_run():
    # Matches "Rajesh Hegde". Starts in middle of run 1, ends inside run 2.
    runs = [
        MockRun("Director is Rajesh"),
        MockRun(" Hegde. Registered office is...")
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    entity = PIIEntity("PERSON", "Rajesh Hegde", 12, 24, 0.90, "presidio")
    
    mapped_runs = map_span_to_runs(12, 24, entity, offsets, runs)
    
    assert len(mapped_runs) == 2
    assert mapped_runs[0].run_index == 0
    assert mapped_runs[0].text_in_run == "Rajesh"
    assert mapped_runs[1].run_index == 1
    assert mapped_runs[1].text_in_run == " Hegde"

def test_pii_ending_mid_run():
    # Matches "Rajesh Hegde". Starts at run 1, ends mid run 2.
    runs = [
        MockRun("Director is "),
        MockRun("Rajesh"),
        MockRun(" Hegde, Whole-time Director")
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    entity = PIIEntity("PERSON", "Rajesh Hegde", 12, 24, 0.90, "presidio")
    
    mapped_runs = map_span_to_runs(12, 24, entity, offsets, runs)
    
    assert len(mapped_runs) == 2
    assert mapped_runs[0].run_index == 1
    assert mapped_runs[0].text_in_run == "Rajesh"
    assert mapped_runs[1].run_index == 2
    assert mapped_runs[1].text_in_run == " Hegde"

def test_multiple_pii_spans_in_one_paragraph():
    runs = [
        MockRun("Contact Alice at alice@example.com.")
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    ent_person = PIIEntity("PERSON", "Alice", 8, 13, 0.90, "presidio")
    ent_email = PIIEntity("EMAIL", "alice@example.com", 17, 34, 0.99, "regex")
    
    mapped_person = map_span_to_runs(8, 13, ent_person, offsets, runs)
    mapped_email = map_span_to_runs(17, 34, ent_email, offsets, runs)
    
    assert len(mapped_person) == 1
    assert mapped_person[0].text_in_run == "Alice"
    assert len(mapped_email) == 1
    assert mapped_email[0].text_in_run == "alice@example.com"

def test_document_location_paths():
    # Body text location
    loc_body = DocumentLocation("body", paragraph_index=15)
    assert loc_body.container_path() == "body / paragraph=15"
    
    # Table cell location
    loc_table = DocumentLocation("table", paragraph_index=0, table_index=2, row_index=3, cell_index=4)
    assert loc_table.container_path() == "table / table=2 / row=3 / cell=4 / paragraph=0"
    
    # Header location
    loc_header = DocumentLocation("header", paragraph_index=1, section_index=0)
    assert loc_header.container_path() == "header / section=0 / paragraph=1"
    
    # Footer location
    loc_footer = DocumentLocation("footer", paragraph_index=2, section_index=1)
    assert loc_footer.container_path() == "footer / section=1 / paragraph=2"

def test_no_match_paragraphs():
    runs = [MockRun("Standard financial document disclaimer.")]
    text, offsets = reconstruct_paragraph_text(runs)
    # No matching PIIEntity is mapped
    mapped_spans = []
    
    loc = DocumentLocation("body", paragraph_index=0)
    mapping = ParagraphMapping(location=loc, text=text, mapped_spans=mapped_spans)
    
    assert len(mapping.mapped_spans) == 0
    assert mapping.location.container_path() == "body / paragraph=0"

def test_formatting_metadata_preservation():
    runs = [
        MockRun("Normal ", bold=False, italic=False),
        MockRun("BoldText", bold=True, italic=False),
        MockRun("ItalicText", bold=False, italic=True)
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    
    # Ensure mapping does not mutate styling metadata
    entity = PIIEntity("GENERIC", "BoldText", 7, 15, 0.80, "regex")
    mapped_runs = map_span_to_runs(7, 15, entity, offsets, runs)
    
    assert len(mapped_runs) == 1
    assert runs[1].bold is True
    assert runs[1].italic is False
    assert runs[2].italic is True

def test_safety_invariant_failure():
    runs = [
        MockRun("Hello "),
        MockRun("World")
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    
    # Text in runs does not match the search term "Word" (missing l)
    entity = PIIEntity("GENERIC", "Word", 6, 10, 0.80, "regex")
    
    with pytest.raises(ValueError, match="Safety Invariant Failed"):
        map_span_to_runs(6, 11, entity, offsets, runs)

def test_reconstruct_paragraph_text_whitespace_normalization():
    runs = [
        MockRun("ICICI\tSecurities"),
        MockRun("\xa0Limited")
    ]
    text, offsets = reconstruct_paragraph_text(runs)
    assert text == "ICICI Securities Limited"
    assert offsets == [
        (0, 16),
        (16, 24)
    ]
