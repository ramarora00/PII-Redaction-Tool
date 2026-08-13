from typing import List
import spacy
from src.detection.base import BaseDetector
from src.detection.models import PIIEntity

class NERDetector(BaseDetector):
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError as e:
            raise RuntimeError(
                "spaCy English model 'en_core_web_sm' is not installed. "
                "Please install it by running the following command in your terminal:\n"
                "  python -m spacy download en_core_web_sm"
            ) from e

    def detect(self, text: str) -> List[PIIEntity]:
        entities: List[PIIEntity] = []
        if not text.strip():
            return entities

        doc = self.nlp(text)
        for ent in doc.ents:
            # Map spaCy NER labels to our standardized PII candidate labels
            if ent.label_ == "PERSON":
                entities.append(PIIEntity(
                    entity_type="PERSON_CANDIDATE",
                    text=ent.text,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.85,
                    source="spacy"
                ))
            elif ent.label_ == "ORG":
                entities.append(PIIEntity(
                    entity_type="COMPANY_CANDIDATE",
                    text=ent.text,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.70,
                    source="spacy"
                ))
            elif ent.label_ in ("GPE", "LOC"):
                entities.append(PIIEntity(
                    entity_type="LOCATION_CANDIDATE",
                    text=ent.text,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.70,
                    source="spacy"
                ))
        return entities
