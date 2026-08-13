from typing import List, Dict, Any, Tuple
from src.detection.models import PIIEntity

# Normalization mapping from detector-specific types to canonical types
CANONICAL_TYPES = {
    "PERSON": "PERSON",
    "PERSON_CANDIDATE": "PERSON",
    
    "EMAIL": "EMAIL",
    "EMAIL_ADDRESS": "EMAIL",
    
    "PHONE": "PHONE",
    "PHONE_NUMBER": "PHONE",
    "PHONE_CANDIDATE": "PHONE",
    
    "SSN": "SSN",
    "US_SSN": "SSN",
    "SSN_CANDIDATE": "SSN",
    
    "CREDIT_CARD": "CREDIT_CARD",
    "CREDIT_CARD_CANDIDATE": "CREDIT_CARD",
    
    "IP_ADDRESS": "IP_ADDRESS",
    "IP_CANDIDATE": "IP_ADDRESS",
    
    "DATE": "DATE",
    "DATE_TIME": "DATE",
    "DATE_CANDIDATE": "DATE",
    
    "DATE_OF_BIRTH": "DATE_OF_BIRTH",
    
    "LOCATION": "LOCATION",
    "LOCATION_CANDIDATE": "LOCATION",
    "GPE": "LOCATION",
    "LOC": "LOCATION",
    
    "COMPANY": "COMPANY",
    "COMPANY_CANDIDATE": "COMPANY",
    "ORG": "COMPANY"
}

# Semantic strength priority mapping (higher is stronger)
TYPE_STRENGTH = {
    "EMAIL": 3,
    "SSN": 3,
    "CREDIT_CARD": 3,
    "IP_ADDRESS": 3,
    
    "DATE_OF_BIRTH": 2,
    "PHONE": 2,
    "DATE": 2,
    
    "PERSON": 1,
    "COMPANY": 1,
    "LOCATION": 1
}

def are_compatible(type_a: str, type_b: str) -> bool:
    """
    Checks if two normalized types are semantically compatible.
    """
    if type_a == type_b:
        return True
    if {type_a, type_b} == {"DATE", "DATE_OF_BIRTH"}:
        return True
    return False

def should_override(c: PIIEntity, r: PIIEntity) -> bool:
    """
    Evaluates whether candidate 'c' should override resolved entity 'r'.
    Returns True if 'c' overrides 'r', False otherwise.
    """
    # 1. Contextual elevation override
    if c.entity_type == "DATE_OF_BIRTH" and r.entity_type == "DATE":
        return True
    if r.entity_type == "DATE_OF_BIRTH" and c.entity_type == "DATE":
        return False
        
    # 2. Check Nesting
    # c is nested in r if r covers c and is strictly larger
    c_in_r = (r.start <= c.start and c.end <= r.end) and (r.start < c.start or c.end < r.end)
    # r is nested in c if c covers r and is strictly larger
    r_in_c = (c.start <= r.start and r.end <= c.end) and (c.start < r.start or r.end < c.end)
    
    compatible = are_compatible(c.entity_type, r.entity_type)
    
    if c_in_r:
        # If compatible, larger span wins (so r wins, c does not override)
        if compatible:
            return False
        # If incompatible, stronger type wins (e.g. nested EMAIL inside PERSON)
        strength_c = TYPE_STRENGTH.get(c.entity_type, 1)
        strength_r = TYPE_STRENGTH.get(r.entity_type, 1)
        if strength_c > strength_r:
            return True
        return False
        
    if r_in_c:
        # If compatible, larger span wins (so c overrides r)
        if compatible:
            return True
        # If incompatible, stronger type wins
        strength_c = TYPE_STRENGTH.get(c.entity_type, 1)
        strength_r = TYPE_STRENGTH.get(r.entity_type, 1)
        if strength_c >= strength_r:
            return True
        return False

    # 3. Non-nested Overlap (e.g. [10:20] and [15:25])
    strength_c = TYPE_STRENGTH.get(c.entity_type, 1)
    strength_r = TYPE_STRENGTH.get(r.entity_type, 1)
    
    if strength_c > strength_r:
        return True
    if strength_r > strength_c:
        return False
        
    # Equal strength: check confidence
    if c.confidence > r.confidence:
        return True
    if r.confidence > c.confidence:
        return False
        
    # Equal confidence: check span length
    len_c = c.end - c.start
    len_r = r.end - r.start
    if len_c > len_r:
        return True
    if len_r > len_c:
        return False
        
    # Deterministic tie break
    if c.start < r.start:
        return True
    if c.start == r.start and c.entity_type < r.entity_type:
        return True
        
    return False

def resolve_candidates(text: str, candidates: List[PIIEntity]) -> List[PIIEntity]:
    """
    Fuses candidate PII entities and resolves conflicts/overlaps according to
    evidence, compatibility, and safety invariants.
    """
    if not candidates:
        return []

    # 1. Safety Invariants & Type Normalization
    normalized: List[PIIEntity] = []
    for c in candidates:
        # Check boundary invariant
        if not (0 <= c.start < c.end <= len(text)):
            raise ValueError(f"Invalid offsets for candidate: {c}. Text length: {len(text)}")
        if text[c.start:c.end] != c.text:
            raise ValueError(f"Candidate text mismatch: '{c.text}' != '{text[c.start:c.end]}' at [{c.start}:{c.end}]")
            
        canonical_type = CANONICAL_TYPES.get(c.entity_type.upper(), c.entity_type.upper())
        normalized.append(PIIEntity(
            entity_type=canonical_type,
            text=c.text,
            start=c.start,
            end=c.end,
            confidence=c.confidence,
            source=c.source,
            metadata=c.metadata
        ))

    # 2. Exact Duplicate Merging (same start, end, type)
    # Group by key
    groups: Dict[Tuple[int, int, str], List[PIIEntity]] = {}
    for cand in normalized:
        key = (cand.start, cand.end, cand.entity_type)
        groups.setdefault(key, []).append(cand)

    merged_candidates: List[PIIEntity] = []
    for key, cands in groups.items():
        start, end, entity_type = key
        # Sort candidates inside group by confidence score descending
        cands.sort(key=lambda x: x.confidence, reverse=True)
        primary = cands[0]
        
        # Build detailed sources metadata array
        sources_provenance = []
        for c in cands:
            sources_provenance.append({
                "source": c.source,
                "confidence": c.confidence,
                "original_type": c.entity_type
            })
            
        merged_candidates.append(PIIEntity(
            entity_type=entity_type,
            text=primary.text,
            start=start,
            end=end,
            confidence=primary.confidence,
            source="fusion",
            metadata={"sources": sources_provenance}
        ))

    # 3. Overlap & Nesting Resolution
    # Sort merged candidates
    # - Primary: start ascending
    # - Secondary: span length descending
    # - Tertiary: type strength descending
    # - Quaternary: confidence descending
    merged_candidates.sort(key=lambda x: (
        x.start,
        -(x.end - x.start),
        -TYPE_STRENGTH.get(x.entity_type, 1),
        -x.confidence,
        x.entity_type
    ))

    resolved_entities: List[PIIEntity] = []
    for c in merged_candidates:
        # Find overlapping elements in resolved_entities
        overlaps = [
            r for r in resolved_entities
            if max(c.start, r.start) < min(c.end, r.end)
        ]
        
        if not overlaps:
            resolved_entities.append(c)
            continue
            
        # c overlaps with one or more resolved entities
        # Check if c overrides ALL overlapping entities
        all_overridden = True
        for r in overlaps:
            if not should_override(c, r):
                all_overridden = False
                break
                
        if all_overridden:
            # Remove overridden ones, insert c
            for r in overlaps:
                resolved_entities.remove(r)
            resolved_entities.append(c)

    # 4. Final Deterministic Ordering
    resolved_entities.sort(key=lambda x: (x.start, x.end, x.entity_type))
    return resolved_entities
