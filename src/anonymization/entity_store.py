import re
import hashlib
from typing import Dict, List, Set, Optional, Tuple
from src.detection.models import PIIEntity
from src.anonymization.generator import SyntheticGenerator

class EntityStore:
    def __init__(self, generator: SyntheticGenerator):
        self.generator = generator
        
        # Maps typed_key (e.g. "PERSON::rajesh hegde") to canonical_id (e.g. "PERSON_001")
        self.key_to_id: Dict[str, str] = {}
        # Maps canonical_id to the primary original text representation
        self.id_to_original: Dict[str, str] = {}
        # Maps canonical_id to its pre-generated synthetic replacement value
        self.id_to_synthetic: Dict[str, str] = {}
        # Counters for each PII type (to generate PERSON_001, etc.)
        self.counters: Dict[str, int] = {}
        # Set of all registered full names (normalized strings)
        self.full_names: Set[str] = set()
        # Maps short names (normalized) to list of matching full names
        self.short_name_matches: Dict[str, List[str]] = {}
        # Maps email canonical ID to person canonical ID (relationship)
        self.email_to_person: Dict[str, str] = {}

    @staticmethod
    def normalize_name(text: str) -> str:
        """
        Normalization: CASING, TRIMMING, and TITLE CLEANUP for comparison.
        """
        cleaned = text.lower()
        # Strip common titles
        titles = [
            r"\bmr\b\.?", r"\bms\b\.?", r"\bmrs\b\.?", r"\bdr\b\.?", 
            r"\bshri\b\.?", r"\bprof\b\.?", r"\bshree\b\.?"
        ]
        for t in titles:
            cleaned = re.sub(t, "", cleaned)
        return " ".join(cleaned.split())

    @staticmethod
    def normalize_general(text: str) -> str:
        """
        Generic normalization for non-name entities.
        """
        return text.strip().lower()

    def _get_next_id(self, entity_type: str) -> str:
        """
        Allocates and increments a deterministic ID (e.g. PERSON_001).
        """
        prefix = entity_type.upper()
        count = self.counters.get(prefix, 0) + 1
        self.counters[prefix] = count
        return f"{prefix}_{count:03d}"

    def register_candidates(self, candidates: List[PIIEntity]) -> None:
        """
        Pass 1: Scans all candidates, registers full names and values.
        """
        # Register full names first to build the base dictionary
        for c in candidates:
            if c.entity_type == "PERSON":
                norm = self.normalize_name(c.text)
                if len(norm.split()) > 1:
                    self.full_names.add(norm)

        # Map non-name candidates and full names to canonical IDs
        for c in candidates:
            # Skip short name candidates for Pass 2
            if c.entity_type == "PERSON":
                norm = self.normalize_name(c.text)
                if len(norm.split()) <= 1:
                    continue
                
                key = f"PERSON::{norm}"
                if key not in self.key_to_id:
                    canonical_id = self._get_next_id("PERSON")
                    self.key_to_id[key] = canonical_id
                    self.id_to_original[canonical_id] = c.text
            else:
                norm = self.normalize_general(c.text)
                key = f"{c.entity_type}::{norm}"
                if key not in self.key_to_id:
                    canonical_id = self._get_next_id(c.entity_type)
                    self.key_to_id[key] = canonical_id
                    self.id_to_original[canonical_id] = c.text

        # Pass 2: Resolve short name aliases conservatively
        for c in candidates:
            if c.entity_type == "PERSON":
                norm = self.normalize_name(c.text)
                if len(norm.split()) > 1:
                    continue  # already registered
                
                key = f"PERSON::{norm}"
                if key in self.key_to_id:
                    continue
                
                # Find matching full names in the store
                matches = [fn for fn in self.full_names if norm in fn.split()]
                if len(matches) == 1:
                    # Unambiguous match! Map short name to the same canonical ID
                    full_key = f"PERSON::{matches[0]}"
                    self.key_to_id[key] = self.key_to_id[full_key]
                else:
                    # Ambiguous (multiple matches or zero matches): treat as new separate entity
                    canonical_id = self._get_next_id("PERSON")
                    self.key_to_id[key] = canonical_id
                    self.id_to_original[canonical_id] = c.text

        # Pass 3: Resolve relationships (email-name mapping)
        # Scan for matching email prefixes
        for c in candidates:
            if c.entity_type == "EMAIL":
                email_norm = self.normalize_general(c.text)
                email_key = f"EMAIL::{email_norm}"
                email_id = self.key_to_id.get(email_key)
                if not email_id or email_id in self.email_to_person:
                    continue
                
                # Extract prefix
                prefix = email_norm.split("@")[0]
                prefix_tokens = set(re.split(r"[._-]", prefix))
                
                # Find matching PERSON
                best_person_id = None
                matches_count = 0
                
                for person_key, person_id in self.key_to_id.items():
                    if not person_key.startswith("PERSON::"):
                        continue
                    person_norm = person_key.split("::", 1)[1]
                    person_tokens = set(person_norm.split())
                    
                    # Conservative check: at least 50% of name tokens exist, or prefix matches first/last name
                    intersection = person_tokens.intersection(prefix_tokens)
                    if intersection and len(intersection) >= min(2, len(person_tokens)):
                        best_person_id = person_id
                        matches_count += 1
                
                if matches_count == 1:
                    # Unambiguous relationship link
                    self.email_to_person[email_id] = best_person_id

    def generate_all_replacements(self) -> None:
        """
        Pre-generates synthetic replacements for all registered canonical IDs,
        ensuring deterministic seeding based on ID, and preserving relationships.
        """
        # 1. Generate PERSON names first (since emails can depend on them)
        person_ids = [cid for cid in self.id_to_original.keys() if cid.startswith("PERSON_")]
        for pid in person_ids:
            if pid not in self.id_to_synthetic:
                self.id_to_synthetic[pid] = self.generator.generate_name(pid)

        # 2. Generate all other replacements
        for cid, original_text in self.id_to_original.items():
            if cid in self.id_to_synthetic:
                continue
                
            if cid.startswith("COMPANY_"):
                self.id_to_synthetic[cid] = self.generator.generate_company(cid)
            elif cid.startswith("EMAIL_"):
                # Check relationship mapping
                linked_person = self.email_to_person.get(cid)
                fake_name = self.id_to_synthetic.get(linked_person) if linked_person else None
                self.id_to_synthetic[cid] = self.generator.generate_email(cid, associated_name=fake_name)
            elif cid.startswith("PHONE_"):
                self.id_to_synthetic[cid] = self.generator.generate_phone(cid, original_text)
            elif cid.startswith("CREDIT_CARD_"):
                self.id_to_synthetic[cid] = self.generator.generate_credit_card(cid, original_text)
            elif cid.startswith("SSN_"):
                self.id_to_synthetic[cid] = self.generator.generate_ssn(cid, original_text)
            elif cid.startswith("IP_ADDRESS_"):
                self.id_to_synthetic[cid] = self.generator.generate_ip(cid, original_text)
            elif cid.startswith("DATE_OF_BIRTH_"):
                self.id_to_synthetic[cid] = self.generator.generate_date(cid, original_text, is_dob=True)
            elif cid.startswith("DATE_"):
                self.id_to_synthetic[cid] = self.generator.generate_date(cid, original_text, is_dob=False)
            elif cid.startswith("ADDRESS_"):
                self.id_to_synthetic[cid] = self.generator.generate_address(cid)
            elif cid.startswith("LOCATION_"):
                self.id_to_synthetic[cid] = self.generator.generate_location(cid)
            else:
                # Default generic string generator
                self.id_to_synthetic[cid] = f"SYNTHETIC_{cid}"

    def get_replacement(self, entity_type: str, original_text: str) -> str:
        """
        Retrieves the deterministic synthetic replacement for the given entity.
        Returns the original text if not found.
        """
        # Resolve key
        if entity_type == "PERSON":
            norm = self.normalize_name(original_text)
        else:
            norm = self.normalize_general(original_text)
            
        key = f"{entity_type}::{norm}"
        canonical_id = self.key_to_id.get(key)
        if not canonical_id:
            return original_text
            
        return self.id_to_synthetic.get(canonical_id, original_text)
