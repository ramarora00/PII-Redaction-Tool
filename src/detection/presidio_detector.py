from typing import List
from presidio_analyzer import AnalyzerEngine
from src.detection.base import BaseDetector
from src.detection.models import PIIEntity

class PresidioDetector(BaseDetector):
    def __init__(self):
        try:
            self.analyzer = AnalyzerEngine()
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Microsoft Presidio Analyzer Engine: {e}. "
                "Ensure that spaCy is correctly installed and the default English model 'en_core_web_sm' "
                "is downloaded by running:\n"
                "  python -m spacy download en_core_web_sm"
            ) from e

    def detect(self, text: str) -> List[PIIEntity]:
        entities: List[PIIEntity] = []
        if not text.strip():
            return entities

        results = self.analyzer.analyze(text=text, language="en")
        
        # Map Presidio entity types to our common PII candidate types
        mapping = {
            "PERSON": "PERSON_CANDIDATE",
            "EMAIL_ADDRESS": "EMAIL",
            "PHONE_NUMBER": "PHONE_CANDIDATE",
            "US_SSN": "SSN_CANDIDATE",
            "CREDIT_CARD": "CREDIT_CARD_CANDIDATE",
            "IP_ADDRESS": "IP_CANDIDATE",
            "DATE_TIME": "DATE_CANDIDATE",
            "LOCATION": "LOCATION_CANDIDATE"
        }

        for res in results:
            standardized_type = mapping.get(res.entity_type)
            if standardized_type:
                entities.append(PIIEntity(
                    entity_type=standardized_type,
                    text=text[res.start:res.end],
                    start=res.start,
                    end=res.end,
                    confidence=res.score,
                    source="presidio"
                ))
        return entities
