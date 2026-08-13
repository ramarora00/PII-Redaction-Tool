from abc import ABC, abstractmethod
from typing import List
from src.detection.models import PIIEntity

class BaseDetector(ABC):
    @abstractmethod
    def detect(self, text: str) -> List[PIIEntity]:
        """
        Parses text and extracts a list of standardized PIIEntity candidates.
        """
        pass
