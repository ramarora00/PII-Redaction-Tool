import re
from typing import List
from src.detection.base import BaseDetector
from src.detection.models import PIIEntity
from src.detection.context_rules import has_dob_context, should_suppress_number

class RegexDetector(BaseDetector):
    def __init__(self):
        # Email pattern
        self.email_pattern = re.compile(
            r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b"
        )
        
        # Phone pattern (matching international and standard 10 digit patterns with strict boundaries)
        # Avoid matching numbers embedded in long strings.
        self.phone_pattern = re.compile(
            r"(?<!\w)\+?\b(?:\d{1,3}[ -.]?)?\(?\d{3}\)?[ -.]?\d{3}[ -.]?\d{4}\b"
        )

        
        # US SSN pattern
        self.ssn_pattern = re.compile(
            r"\b\d{3}-\d{2}-\d{4}\b"
        )
        
        # Credit Card pattern (matches digits or hyphens grouped standard way)
        self.cc_pattern = re.compile(
            r"\b(?:\d[ -]?){13,19}\b"
        )
        
        # IP Address patterns (IPv4 and a simplified IPv6)
        self.ipv4_pattern = re.compile(
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        )
        self.ipv6_pattern = re.compile(
            r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b"
        )
        
        # Generic date pattern (formats like 01-02-2005, 2005/01/02, etc.)
        self.date_pattern = re.compile(
            r"\b(?:\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\b"
        )

        # Registry / corporate entities pattern to capture full spans (resolves punctuation/comma splits)
        self.registry_pattern = re.compile(
            r"\b(?:Registrar of Companies\s*Central Processing Centre|Registrar of Companies(?:,\s*Central Processing Centre)|Registrar of Companies\s*Maharashtra|Registrar of Companies(?:,\s*Maharashtra)?|RoC|ROC)\b",
            re.IGNORECASE
        )

    @staticmethod
    def is_valid_luhn(card_str: str) -> bool:
        """
        Performs Luhn checksum validation.
        """
        digits = [int(c) for c in card_str if c.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        
        # Luhn Algorithm
        checksum = 0
        reverse_digits = digits[::-1]
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 1:
                double_digit = digit * 2
                if double_digit > 9:
                    double_digit -= 9
                checksum += double_digit
            else:
                checksum += digit
        return checksum % 10 == 0

    def detect(self, text: str) -> List[PIIEntity]:
        entities: List[PIIEntity] = []
        
        # 1. Emails
        for m in self.email_pattern.finditer(text):
            entities.append(PIIEntity(
                entity_type="EMAIL",
                text=m.group(),
                start=m.start(),
                end=m.end(),
                confidence=0.99,
                source="regex"
            ))

        # 2. Phone Candidates (suppress common non-phone numeric identifiers)
        for m in self.phone_pattern.finditer(text):
            start, end = m.start(), m.end()
            raw_text = m.group()
            # Clean non-digit characters to check digit count
            digit_count = len([c for c in raw_text if c.isdigit()])
            if 7 <= digit_count <= 15:
                if not should_suppress_number(text, start):
                    entities.append(PIIEntity(
                        entity_type="PHONE_CANDIDATE",
                        text=raw_text,
                        start=start,
                        end=end,
                        confidence=0.85,
                        source="regex"
                    ))

        # 3. SSN
        for m in self.ssn_pattern.finditer(text):
            entities.append(PIIEntity(
                entity_type="SSN_CANDIDATE",
                text=m.group(),
                start=m.start(),
                end=m.end(),
                confidence=0.95,
                source="regex"
            ))

        # 4. Credit Card (requires structural regex match + Luhn validation + suppression check)
        for m in self.cc_pattern.finditer(text):
            start, end = m.start(), m.end()
            raw_text = m.group()
            # Strip non-digit characters for Luhn validation
            clean_digits = "".join(c for c in raw_text if c.isdigit())
            if self.is_valid_luhn(clean_digits):
                if not should_suppress_number(text, start):
                    entities.append(PIIEntity(
                        entity_type="CREDIT_CARD_CANDIDATE",
                        text=raw_text,
                        start=start,
                        end=end,
                        confidence=0.90,
                        source="regex"
                    ))

        # 5. IP Addresses
        for m in self.ipv4_pattern.finditer(text):
            entities.append(PIIEntity(
                entity_type="IP_CANDIDATE",
                text=m.group(),
                start=m.start(),
                end=m.end(),
                confidence=0.95,
                source="regex"
            ))
            
        for m in self.ipv6_pattern.finditer(text):
            entities.append(PIIEntity(
                entity_type="IP_CANDIDATE",
                text=m.group(),
                start=m.start(),
                end=m.end(),
                confidence=0.95,
                source="regex"
            ))

        # 6. Dates (Contextual logic checks if this is DOB or general Date)
        for m in self.date_pattern.finditer(text):
            start, end = m.start(), m.end()
            raw_text = m.group()
            
            # Check context window for DOB keywords
            if has_dob_context(text, start, end):
                entities.append(PIIEntity(
                    entity_type="DATE_OF_BIRTH",
                    text=raw_text,
                    start=start,
                    end=end,
                    confidence=0.90,
                    source="regex"
                ))
            else:
                entities.append(PIIEntity(
                    entity_type="DATE_CANDIDATE",
                    text=raw_text,
                    start=start,
                    end=end,
                    confidence=0.50,
                    source="regex"
                ))

        # 7. Registries
        for m in self.registry_pattern.finditer(text):
            entities.append(PIIEntity(
                entity_type="COMPANY_CANDIDATE",
                text=m.group(),
                start=m.start(),
                end=m.end(),
                confidence=0.95,
                source="regex"
            ))

        return entities
