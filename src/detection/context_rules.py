import re
from typing import List

# Keywords indicating Date of Birth context
DOB_KEYWORDS = ["birth", "dob", "born", "date of birth", "d.o.b"]

# Keywords indicating non-PII numeric identifiers that should suppress phone/card candidates
SUPPRESSION_KEYWORDS = [
    r"order\s+(?:no|num|number)",
    r"ticket\s+(?:no|num|number)",
    r"invoice\s+(?:no|num|number)",
    r"reference\s+(?:no|num|number)",
    r"application\s+(?:no|num|number)",
    r"page\s+(?:no|num|number)",
    r"folio\s+(?:no|num|number)",
    r"table\s+(?:no|num|number)",
    r"serial\s+(?:no|num|number)"
]

def has_dob_context(text: str, start: int, end: int, window: int = 50) -> bool:
    """
    Checks if a match at text[start:end] is surrounded by DOB keywords.
    We inspect 'window' characters before the start index.
    """
    left_context = text[max(0, start - window):start].lower()
    right_context = text[end:min(len(text), end + window)].lower()
    
    combined_context = left_context + " " + right_context
    for kw in DOB_KEYWORDS:
        if kw in combined_context:
            return True
    return False

def should_suppress_number(text: str, start: int, window: int = 40) -> bool:
    """
    Checks if a number matched at start is preceded by suppression keywords.
    We inspect 'window' characters before the start index.
    """
    left_context = text[max(0, start - window):start].lower()
    for kw in SUPPRESSION_KEYWORDS:
        if re.search(kw, left_context):
            return True
    return False
