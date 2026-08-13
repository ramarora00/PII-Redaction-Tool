import hashlib
import random
import re
from typing import Dict, Set, Optional
from faker import Faker

class SyntheticGenerator:
    def __init__(self, locale: str = "en_IN"):
        self.locale = locale
        self.faker = Faker(locale)
        self.used_values: Set[str] = set()

    def _get_seeded_rng(self, canonical_id: str) -> random.Random:
        """
        Creates a deterministic Random instance seeded with the hash of the canonical_id.
        """
        seed_hash = hashlib.md5(canonical_id.encode("utf-8")).hexdigest()
        seed = int(seed_hash, 16) % 1000000
        return random.Random(seed)

    def generate_name(self, canonical_id: str) -> str:
        """
        Generates a deterministic synthetic name. Avoids collisions.
        """
        rng = self._get_seeded_rng(canonical_id)
        # Seed faker instance
        self.faker.seed_instance(rng.randint(0, 1000000))
        
        # In case of collisions, increment and try again
        attempts = 0
        while True:
            fake_name = self.faker.name()
            # Ensure uniqueness across different canonical IDs (not same ID)
            # If we query the same ID twice, it returns the same name (handled by entity store cache).
            if fake_name not in self.used_values:
                self.used_values.add(fake_name)
                return fake_name
            
            # Increment seed to resolve collision
            attempts += 1
            self.faker.seed_instance(rng.randint(0, 1000000) + attempts)
            if attempts > 100:
                # Fallback to appending a unique index
                return f"{fake_name} {attempts}"

    def generate_company(self, canonical_id: str) -> str:
        """
        Generates a deterministic synthetic company name.
        """
        rng = self._get_seeded_rng(canonical_id)
        self.faker.seed_instance(rng.randint(0, 1000000))
        
        attempts = 0
        while True:
            fake_company = self.faker.company()
            if fake_company not in self.used_values:
                self.used_values.add(fake_company)
                return fake_company
            attempts += 1
            self.faker.seed_instance(rng.randint(0, 1000000) + attempts)
            if attempts > 100:
                return f"{fake_company} {attempts}"

    def generate_email(self, canonical_id: str, associated_name: Optional[str] = None) -> str:
        """
        Generates a deterministic synthetic email. If an associated fake name is provided,
        uses it to create a realistic linked email prefix.
        """
        if associated_name:
            # Slugify name
            clean_name = re.sub(r"[^a-zA-Z0-9]", ".", associated_name.lower())
            fake_email = f"{clean_name}@example.com"
            return fake_email

        rng = self._get_seeded_rng(canonical_id)
        self.faker.seed_instance(rng.randint(0, 1000000))
        return self.faker.email()

    def generate_phone(self, canonical_id: str, original_text: str) -> str:
        """
        Generates a deterministic synthetic phone number preserving the exact structural layout
        (spacing, punctuation, country codes) by mapping digits randomly.
        """
        rng = self._get_seeded_rng(canonical_id)
        result = []
        for char in original_text:
            if char.isdigit():
                # Replace digit deterministically
                result.append(str(rng.randint(0, 9)))
            else:
                result.append(char)
        return "".join(result)

    def generate_credit_card(self, canonical_id: str, original_text: str) -> str:
        """
        Generates a fully synthetic, Luhn-valid card number preserving length and spaces/dashes,
        but without leaking the original BIN/network prefix.
        """
        rng = self._get_seeded_rng(canonical_id)
        # Count clean digits
        clean_len = len([c for c in original_text if c.isdigit()])
        if clean_len < 13:
            clean_len = 16
            
        # Generate clean_len - 1 random digits
        digits = [rng.randint(0, 9) for _ in range(clean_len - 1)]
        
        # Calculate Luhn check digit
        total = 0
        for idx, digit in enumerate(reversed(digits)):
            if idx % 2 == 0:
                val = digit * 2
                if val > 9:
                    val -= 9
                total += val
            else:
                total += digit
        check_digit = (10 - (total % 10)) % 10
        digits.append(check_digit)
        
        # Map digits back into original spacing/punctuation
        digit_idx = 0
        result = []
        for char in original_text:
            if char.isdigit():
                if digit_idx < len(digits):
                    result.append(str(digits[digit_idx]))
                    digit_idx += 1
            else:
                result.append(char)
        
        # Append remaining digits if spacing was short
        while digit_idx < len(digits):
            result.append(str(digits[digit_idx]))
            digit_idx += 1
            
        return "".join(result)

    def generate_ssn(self, canonical_id: str, original_text: str) -> str:
        """
        Generates a formatted fake SSN matching original layout (e.g. XXX-XX-XXXX).
        """
        rng = self._get_seeded_rng(canonical_id)
        result = []
        for char in original_text:
            if char.isdigit():
                result.append(str(rng.randint(0, 9)))
            else:
                result.append(char)
        return "".join(result)

    def generate_ip(self, canonical_id: str, original_text: str) -> str:
        """
        Generates standard IPv4/IPv6 values preserving structural layout.
        """
        rng = self._get_seeded_rng(canonical_id)
        if ":" in original_text:
            # IPv6
            parts = [f"{rng.randint(0, 65535):x}" for _ in range(8)]
            return ":".join(parts)
        else:
            # IPv4
            parts = [str(rng.randint(0, 255)) for _ in range(4)]
            return ".".join(parts)

    def generate_date(self, canonical_id: str, original_text: str, is_dob: bool = False) -> str:
        """
        Generates a deterministic synthetic date, matching the format layout of the original text.
        If is_dob is True, generates a date corresponding to a typical date of birth (18+ years ago).
        """
        rng = self._get_seeded_rng(canonical_id)
        
        # Generate random year, month, day
        if is_dob:
            year = rng.randint(1960, 2005)
        else:
            year = rng.randint(2010, 2026)
            
        month = rng.randint(1, 12)
        day = rng.randint(1, 28)  # safe day limit
        
        # Identify separator
        separator = "-"
        for sep in ["/", ".", "-"]:
            if sep in original_text:
                separator = sep
                break
                
        # Match original format ordering (e.g. YYYY/MM/DD vs DD-MM-YYYY)
        # Split by separator
        parts = original_text.split(separator)
        if len(parts) != 3:
            # Fallback
            return f"{day:02d}{separator}{month:02d}{separator}{year}"
            
        result = []
        for part in parts:
            part_clean = part.strip()
            if len(part_clean) == 4:
                result.append(f"{year:04d}")
            elif len(part_clean) == 2:
                # Could be month or day
                if part_clean == parts[0]:
                    # Assume day first
                    result.append(f"{day:02d}")
                else:
                    result.append(f"{month:02d}")
            else:
                result.append(f"{day:02d}")
                
        return separator.join(result)

    def generate_address(self, canonical_id: str) -> str:
        """
        Generates a deterministic synthetic physical/mailing address.
        """
        rng = self._get_seeded_rng(canonical_id)
        self.faker.seed_instance(rng.randint(0, 1000000))
        # Replace newlines with comma-space to match inline structure
        fake_address = self.faker.address().replace('\n', ', ')
        return fake_address

    def generate_location(self, canonical_id: str) -> str:
        """
        Generates a deterministic synthetic location.
        """
        rng = self._get_seeded_rng(canonical_id)
        self.faker.seed_instance(rng.randint(0, 1000000))
        return self.faker.city()
