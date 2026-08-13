import re
from typing import List
from src.detection.models import PIIEntity

class CandidateValidator:
    def __init__(self):
        # Generic document terminology (lowercase for matching)
        self.generic_terms = {
            "offer", "prospectus", "board", "table", "anchor investors",
            "issue", "promoters", "red herring prospectus"
        }
        
        # Personal titles/indicators
        self.personal_indicators = {
            "mr", "ms", "mrs", "shri", "shree", "dr", "prof", 
            "contact", "secretary", "officer", "chairman", "director", "person"
        }

        # Strong technical standards and document labels (excluding generic 'standard')
        self.strong_tech_labels = {
            "iatf", "iso", "bs", "en", "page", "order", "invoice", 
            "ticket", "reference", "folio", "application", "no", "no."
        }

        # Currency and financial markers
        self.currency_markers = {"rs", "rs.", "rupees", "usd", "aud", "inr", "$"}
        self.scale_qualifiers = {"crore", "lakh", "million", "billion"}

        # Regulatory acronyms and corporate roles (lowercase for matching)
        self.regulatory_acronyms = {"scra", "scrr", "icdr", "sebi", "bse", "nse", "rbi", "roc"}
        self.corporate_roles = {
            "director", "directors", "promoter", "promoters", "chairman",
            "board", "company", "registrar", "regulations", "act", "depositories act"
        }

    def validate_candidates(self, text: str, candidates: List[PIIEntity]) -> List[PIIEntity]:
        """
        Coordinates the execution of specialized validation rules over deconflicted entities.
        Saves decision KEEP/REJECT and reason inside entity metadata.
        """
        validated_list = []
        for cand in candidates:
            # Set default validation metadata
            if cand.metadata is None:
                cand.metadata = {}
            if "validation_decision" not in cand.metadata:
                cand.metadata["validation_decision"] = "KEEP"
            if "validation_reason" not in cand.metadata:
                cand.metadata["validation_reason"] = "GENUINE_PII"

            # Apply validation filters sequentially
            self._validate_generic_terms(text, cand)
            self._validate_address_vs_person(text, cand)
            self._validate_numeric_standards(text, cand)
            self._validate_financial_numbers(text, cand)
            self._validate_regulatory_and_corporate(text, cand)

            validated_list.append(cand)
        return validated_list

    def _validate_generic_terms(self, text: str, cand: PIIEntity) -> None:
        """
        Filters out common document keywords matching PERSON or COMPANY unless preceded by personal context.
        """
        if cand.entity_type not in ("PERSON", "COMPANY"):
            return

        cand_clean = cand.text.strip().lower()
        # Check if the text matches a generic document term or is nested inside one
        is_generic = any(term == cand_clean or term in cand_clean for term in self.generic_terms)
        
        if is_generic:
            # Check context prefix (up to 30 characters before)
            start_window = max(0, cand.start - 30)
            prefix_window = text[start_window:cand.start].lower()
            prefix_tokens = set(re.findall(r"\b\w+\b", prefix_window))
            
            # If personal context exists, KEEP. Otherwise, REJECT.
            has_personal_context = any(ind in prefix_tokens for ind in self.personal_indicators)
            
            if not has_personal_context:
                cand.metadata["validation_decision"] = "REJECT"
                cand.metadata["validation_reason"] = "GENERIC_DOCUMENT_TERM"

    def _validate_address_vs_person(self, text: str, cand: PIIEntity) -> None:
        """
        Filters out PERSON candidates that are actually regional address markers
        by scanning for multiple strong address signals in a 50-character window.
        """
        if cand.entity_type != "PERSON":
            return

        # 50-character context window around the entity
        start_w = max(0, cand.start - 50)
        end_w = min(len(text), cand.end + 50)
        context = text[start_w:end_w].lower()

        address_signals = {
            "village", "taluka", "district", "street", "road", "nagar",
            "pin", "postal", "maharashtra", "office", "registered office"
        }
        
        # Count matching signals
        tokens = set(re.findall(r"\b\w+\b", context))
        matching_signals = address_signals.intersection(tokens)
        signal_count = len(matching_signals)

        # Check for 6-digit PIN code matching
        if re.search(r"\b\d{6}\b", context):
            signal_count += 1

        # Reject if 2 or more distinct address signals are present
        if signal_count >= 2:
            cand.metadata["validation_decision"] = "REJECT"
            cand.metadata["validation_reason"] = "ADDRESS_CONTEXT"

    def _validate_numeric_standards(self, text: str, cand: PIIEntity) -> None:
        """
        Suppresses numbers parsed as PHONE if they are preceded by strong technical or document labels.
        """
        if cand.entity_type != "PHONE":
            return

        # 25-character prefix context scan
        start_w = max(0, cand.start - 25)
        prefix_context = text[start_w:cand.start].lower()
        prefix_tokens = set(re.findall(r"\b\w+\b", prefix_context))

        # Check if any strong technical label matches the context tokens
        has_tech_label = any(label in prefix_tokens for label in self.strong_tech_labels)
        
        if has_tech_label:
            cand.metadata["validation_decision"] = "REJECT"
            cand.metadata["validation_reason"] = "TECHNICAL_STANDARD"

    def _validate_financial_numbers(self, text: str, cand: PIIEntity) -> None:
        """
        Suppresses numbers matched as PHONE or CREDIT_CARD if they are surrounded
        by currency markers or scale scale qualifiers.
        """
        if cand.entity_type not in ("PHONE", "CREDIT_CARD"):
            return

        # Scan 20 characters before for currency
        start_prefix = max(0, cand.start - 20)
        prefix = text[start_prefix:cand.start].lower()
        has_currency = any(curr in prefix for curr in self.currency_markers)

        # Scan 20 characters after for scale
        end_suffix = min(len(text), cand.end + 20)
        suffix = text[cand.end:end_suffix].lower()
        has_scale = any(scale in suffix for scale in self.scale_qualifiers)

        if has_currency or has_scale:
            cand.metadata["validation_decision"] = "REJECT"
            cand.metadata["validation_reason"] = "FINANCIAL_CONTEXT"
