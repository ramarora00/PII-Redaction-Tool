from dataclasses import dataclass
from typing import Optional, List
from src.detection.models import PIIEntity

@dataclass
class DocumentLocation:
    location_type: str  # "body", "table", "header", "footer"
    paragraph_index: int
    section_index: Optional[int] = None
    table_index: Optional[int] = None
    row_index: Optional[int] = None
    cell_index: Optional[int] = None

    def container_path(self) -> str:
        """
        Generates an unambiguous, unique path representing the paragraph location.
        """
        if self.location_type == "body":
            return f"body / paragraph={self.paragraph_index}"
        elif self.location_type == "table":
            return f"table / table={self.table_index} / row={self.row_index} / cell={self.cell_index} / paragraph={self.paragraph_index}"
        elif self.location_type == "header":
            return f"header / section={self.section_index} / paragraph={self.paragraph_index}"
        elif self.location_type == "footer":
            return f"footer / section={self.section_index} / paragraph={self.paragraph_index}"
        return f"unknown / paragraph={self.paragraph_index}"

@dataclass
class MappedRunSpan:
    run_index: int
    start_in_run: int
    end_in_run: int
    text_in_run: str

@dataclass
class MappedPIISpan:
    entity: PIIEntity
    run_spans: List[MappedRunSpan]

@dataclass
class ParagraphMapping:
    location: DocumentLocation
    text: str
    mapped_spans: List[MappedPIISpan]
