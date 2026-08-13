from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class PIIEntity:
    entity_type: str
    text: str
    start: int
    end: int
    confidence: float
    source: str
    metadata: Optional[Dict[str, Any]] = None
