"""
Mock API implementations for external integrations.
Simulates RxNorm, MedDRA, and PV Case Management System APIs with realistic responses.
"""

import hashlib
import time
from typing import Optional, Dict, List, Any
from dataclasses import dataclass


@dataclass
class APIResponse:
    """Generic API response wrapper"""
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class MockRxNormAPI:
    """
    Mock RxNorm API for drug nomenclature normalization.
    Simulates https://rxnav.nlm.nih.gov/REST/rxcui.json
    """

    # Static drug name to RxCUI mapping
    DRUG_DATABASE = {
        "tezarimab": {"rxcui": "123456", "name": "tezarimab"},
        "solivian": {"rxcui": "789012", "name": "solivimab"},
        "solivimab": {"rxcui": "789012", "name": "solivimab"},
        "phaedora": {"rxcui": "345678", "name": "phaedexine"},
        "phaedexine": {"rxcui": "345678", "name": "phaedexine"},
        "ibuprofen": {"rxcui": "5640", "name": "ibuprofen"},
        "acetaminophen": {"rxcui": "161", "name": "acetaminophen"},
        "levothyroxine": {"rxcui": "10582", "name": "levothyroxine"},
        "vitamin d3": {"rxcui": "2116", "name": "cholecalciferol"},
        "adderall": {"rxcui": "861634", "name": "amphetamine/dextroamphetamine"},
    }

    def __init__(self, simulate_failures: bool = False):
        self.simulate_failures = simulate_failures
        self.request_count = 0

    def lookup_rxcui(self, drug_name: str) -> APIResponse:
        """
        Lookup RxCUI code for drug name.
        Returns: APIResponse with rxcui or 404 if not found.
        """
        self.request_count += 1

        # Simulate rate limiting (20 req/sec limit)
        if self.simulate_failures and self.request_count % 25 == 0:
            return APIResponse(
                status_code=429,
                error_message="Rate limit exceeded (20 req/sec)"
            )

        # Simulate occasional API failures
        if self.simulate_failures and self.request_count % 50 == 0:
            return APIResponse(
                status_code=500,
                error_message="RxNorm API internal error"
            )

        # Normalize drug name for lookup
        normalized_name = drug_name.lower().strip()

        # Check database
        if normalized_name in self.DRUG_DATABASE:
            drug_data = self.DRUG_DATABASE[normalized_name]
            return APIResponse(
                status_code=200,
                data={
                    "idGroup": {
                        "rxnormId": [drug_data["rxcui"]],
                        "name": drug_data["name"]
                    }
                }
            )

        # Drug not found
        return APIResponse(
            status_code=404,
            error_message=f"Drug '{drug_name}' not found in RxNorm database"
        )


class MockMedDRAAPI:
    """
    Mock MedDRA API for adverse event term coding.
    Simulates MedDRA PT (Preferred Term) lookup.
    """

    # Static AE term to MedDRA PT mapping
    MEDDRA_DATABASE = {
        "headache": {"pt": "Headache", "code": "10019211", "soc": "Nervous system disorders"},
        "severe headache": {"pt": "Headache", "code": "10019211", "soc": "Nervous system disorders"},
        "migraine": {"pt": "Migraine", "code": "10027599", "soc": "Nervous system disorders"},
        "visual disturbance": {"pt": "Visual impairment", "code": "10047571", "soc": "Eye disorders"},
        "blurred vision": {"pt": "Vision blurred", "code": "10047513", "soc": "Eye disorders"},
        "sweating": {"pt": "Hyperhidrosis", "code": "10020642", "soc": "Skin and subcutaneous tissue disorders"},
        "excessive sweating": {"pt": "Hyperhidrosis", "code": "10020642", "soc": "Skin and subcutaneous tissue disorders"},
        "hyperhidrosis": {"pt": "Hyperhidrosis", "code": "10020642", "soc": "Skin and subcutaneous tissue disorders"},
        "heart racing": {"pt": "Palpitations", "code": "10033557", "soc": "Cardiac disorders"},
        "palpitations": {"pt": "Palpitations", "code": "10033557", "soc": "Cardiac disorders"},
        "panic attack": {"pt": "Panic attack", "code": "10033664", "soc": "Psychiatric disorders"},
        "shakiness": {"pt": "Tremor", "code": "10044565", "soc": "Nervous system disorders"},
        "tremor": {"pt": "Tremor", "code": "10044565", "soc": "Nervous system disorders"},
        "elevated liver enzymes": {"pt": "Hepatic enzyme increased", "code": "10060795", "soc": "Investigations"},
        "liver enzyme elevation": {"pt": "Hepatic enzyme increased", "code": "10060795", "soc": "Investigations"},
        "hepatic enzyme increased": {"pt": "Hepatic enzyme increased", "code": "10060795", "soc": "Investigations"},
        "drug-induced liver injury": {"pt": "Drug-induced liver injury", "code": "10059093", "soc": "Hepatobiliary disorders"},
        "hepatotoxicity": {"pt": "Hepatotoxicity", "code": "10019851", "soc": "Hepatobiliary disorders"},
        "nausea": {"pt": "Nausea", "code": "10028813", "soc": "Gastrointestinal disorders"},
        "vomiting": {"pt": "Vomiting", "code": "10047700", "soc": "Gastrointestinal disorders"},
        "diarrhea": {"pt": "Diarrhoea", "code": "10012735", "soc": "Gastrointestinal disorders"},
        "fatigue": {"pt": "Fatigue", "code": "10016256", "soc": "General disorders and administration site conditions"},
        "weakness": {"pt": "Asthenia", "code": "10003549", "soc": "General disorders and administration site conditions"},
        "rash": {"pt": "Rash", "code": "10037844", "soc": "Skin and subcutaneous tissue disorders"},
        "pruritus": {"pt": "Pruritus", "code": "10037087", "soc": "Skin and subcutaneous tissue disorders"},
        "dizziness": {"pt": "Dizziness", "code": "10013573", "soc": "Nervous system disorders"},
        "insomnia": {"pt": "Insomnia", "code": "10022437", "soc": "Psychiatric disorders"},
    }

    def __init__(self, simulate_failures: bool = False):
        self.simulate_failures = simulate_failures
        self.request_count = 0
        self.api_key_valid = True

    def search_preferred_term(self, ae_term: str) -> APIResponse:
        """
        Search for MedDRA Preferred Term.
        Returns: APIResponse with PT, code, and SOC or 404 if not found.
        """
        self.request_count += 1

        # Simulate auth failure (license expired)
        if self.simulate_failures and not self.api_key_valid:
            return APIResponse(
                status_code=401,
                error_message="MedDRA API authentication failed (license expired or invalid API key)"
            )

        # Simulate rate limiting (100 req/min)
        if self.simulate_failures and self.request_count % 105 == 0:
            return APIResponse(
                status_code=429,
                error_message="Rate limit exceeded (100 req/min)"
            )

        # Normalize AE term for lookup
        normalized_term = ae_term.lower().strip()

        # Check database - exact match first
        if normalized_term in self.MEDDRA_DATABASE:
            meddra_data = self.MEDDRA_DATABASE[normalized_term]
            return APIResponse(
                status_code=200,
                data={
                    "preferred_term": meddra_data["pt"],
                    "meddra_code": meddra_data["code"],
                    "soc": meddra_data["soc"]
                }
            )

        # Keyword matching - check if any database term appears in the input
        # (Simulates real MedDRA NLP/keyword extraction)
        for db_term, meddra_data in self.MEDDRA_DATABASE.items():
            # Check if database term appears as a word in the input
            # Use word boundaries to avoid false matches (e.g., "head" in "headache")
            import re
            pattern = r'\b' + re.escape(db_term) + r'\b'
            if re.search(pattern, normalized_term):
                return APIResponse(
                    status_code=200,
                    data={
                        "preferred_term": meddra_data["pt"],
                        "meddra_code": meddra_data["code"],
                        "soc": meddra_data["soc"]
                    }
                )

        # Term not found
        return APIResponse(
            status_code=404,
            error_message=f"AE term '{ae_term}' not found in MedDRA database"
        )

    def revoke_api_key(self):
        """Simulate license expiration for testing"""
        self.api_key_valid = False

    def restore_api_key(self):
        """Restore API key for testing"""
        self.api_key_valid = True

    def search_hierarchy(self, ae_term: str, search_type: str = "exact") -> APIResponse:
        """
        Search MedDRA hierarchy for related terms.
        search_type: "exact", "synonym", "broader", "narrower"
        Returns: APIResponse with matching terms and relationship type.
        """
        self.request_count += 1

        normalized_term = ae_term.lower().strip()

        # Exact match first
        if normalized_term in self.MEDDRA_DATABASE:
            exact_data = self.MEDDRA_DATABASE[normalized_term]

            if search_type == "exact":
                return APIResponse(
                    status_code=200,
                    data={
                        "preferred_term": exact_data["pt"],
                        "meddra_code": exact_data["code"],
                        "soc": exact_data["soc"],
                        "match_type": "exact"
                    }
                )

        # Synonym matching (simple keyword overlap)
        if search_type == "synonym":
            for term, data in self.MEDDRA_DATABASE.items():
                # Simple synonym logic: shared significant words
                ae_words = set(normalized_term.split())
                db_words = set(term.split())
                overlap = ae_words.intersection(db_words)

                if overlap and term != normalized_term:
                    return APIResponse(
                        status_code=200,
                        data={
                            "preferred_term": data["pt"],
                            "meddra_code": data["code"],
                            "soc": data["soc"],
                            "match_type": "synonym",
                            "matched_term": term
                        }
                    )

        # Broader term (map to SOC)
        if search_type == "broader" and normalized_term in self.MEDDRA_DATABASE:
            data = self.MEDDRA_DATABASE[normalized_term]
            return APIResponse(
                status_code=200,
                data={
                    "broader_term": data["soc"],
                    "match_type": "broader"
                }
            )

        # Narrower term (simplified: look for terms containing this as substring)
        if search_type == "narrower":
            narrower_matches = []
            for term, data in self.MEDDRA_DATABASE.items():
                if normalized_term in term and term != normalized_term:
                    narrower_matches.append({
                        "preferred_term": data["pt"],
                        "meddra_code": data["code"],
                        "soc": data["soc"]
                    })

            if narrower_matches:
                return APIResponse(
                    status_code=200,
                    data={
                        "narrower_terms": narrower_matches,
                        "match_type": "narrower"
                    }
                )

        # Not found
        return APIResponse(
            status_code=404,
            error_message=f"No {search_type} match found for '{ae_term}'"
        )


class MockPVCaseManagementAPI:
    """
    Mock PV Case Management System API.
    Simulates case read (duplicate detection) and write operations.
    """

    def __init__(self, simulate_failures: bool = False):
        self.simulate_failures = simulate_failures
        self.case_database: Dict[str, Dict[str, Any]] = {}
        self.write_count = 0
        self.service_available = True

    def write_case(self, case_data: Dict[str, Any]) -> APIResponse:
        """
        Write AECasePackage to PV system.
        Returns: APIResponse with case_id or error.
        """
        self.write_count += 1

        # Simulate service unavailability (503)
        if self.simulate_failures and not self.service_available:
            return APIResponse(
                status_code=503,
                error_message="PV Case Management API temporarily unavailable"
            )

        # Simulate occasional timeouts
        if self.simulate_failures and self.write_count % 30 == 0:
            return APIResponse(
                status_code=504,
                error_message="Gateway timeout"
            )

        # Validate required fields
        if "case_id" not in case_data:
            return APIResponse(
                status_code=400,
                error_message="Missing required field: case_id"
            )

        case_id = case_data["case_id"]

        # Idempotency check: if case_id exists, return existing record
        if case_id in self.case_database:
            return APIResponse(
                status_code=200,
                data={
                    "status": "exists",
                    "case_id": case_id,
                    "message": "Case already exists (idempotent write)"
                }
            )

        # Write case to database
        self.case_database[case_id] = case_data

        return APIResponse(
            status_code=201,
            data={
                "status": "created",
                "case_id": case_id,
                "received_at": case_data.get("received_at")
            }
        )

    def search_duplicates(
        self,
        patient_name: Optional[str] = None,
        drug_name: Optional[str] = None,
        ae_term: Optional[str] = None,
        date_range_days: int = 30
    ) -> APIResponse:
        """
        Search for potential duplicate cases.
        Returns: APIResponse with list of matching cases and fuzzy match scores.
        """

        # Simple fuzzy match simulation (not production-grade)
        matches = []

        for case_id, case in self.case_database.items():
            match_score = 0.0
            match_count = 0

            # Check patient match (simplified)
            if patient_name and "patient" in case:
                # In real implementation, use Levenshtein distance
                match_count += 1
                if patient_name.lower() in str(case.get("patient", {})).lower():
                    match_score += 0.4

            # Check drug match
            if drug_name and "suspect_drug" in case:
                match_count += 1
                case_drug = case["suspect_drug"].get("name", "").lower()
                if drug_name.lower() == case_drug:
                    match_score += 0.4

            # Check AE term match
            if ae_term and "ae_description" in case:
                match_count += 1
                case_ae = case["ae_description"].get("narrative", "").lower()
                if ae_term.lower() in case_ae:
                    match_score += 0.2

            # Normalize score
            if match_count > 0:
                final_score = match_score
                if final_score > 0.5:
                    matches.append({
                        "case_id": case_id,
                        "fuzzy_match_score": final_score,
                        "received_at": case.get("received_at")
                    })

        return APIResponse(
            status_code=200,
            data={
                "matches": matches,
                "total_count": len(matches)
            }
        )

    def set_service_unavailable(self):
        """Simulate service outage for testing"""
        self.service_available = False

    def restore_service(self):
        """Restore service for testing"""
        self.service_available = True

    def search_signal_pattern(
        self,
        product_name: str,
        ae_term: str,
        lookback_days: int = 90
    ) -> APIResponse:
        """
        Search for signal detection pattern (FDA Requirement 3).
        Looks for 3+ cases with same product + AE term within lookback_days.
        Returns: APIResponse with matching cases and signal flag.
        """
        from datetime import datetime, timedelta

        matches = []
        cutoff_date = datetime.now() - timedelta(days=lookback_days)

        for case_id, case in self.case_database.items():
            # Check if case matches product + AE term
            case_drug = case.get("suspect_drug", {}).get("name", "").lower()
            case_ae = case.get("ae_description", {}).get("narrative", "").lower()
            case_received = case.get("received_at", "")

            # Parse received_at
            try:
                case_date = datetime.fromisoformat(case_received.replace("Z", "+00:00"))
            except Exception:
                continue

            # Check if within lookback window
            if case_date < cutoff_date:
                continue

            # Check product match
            if product_name.lower() not in case_drug:
                continue

            # Check AE term match (substring)
            if ae_term.lower() not in case_ae:
                continue

            matches.append({
                "case_id": case_id,
                "received_at": case_received,
                "product": case.get("suspect_drug", {}).get("name"),
                "ae_term": case.get("ae_description", {}).get("narrative")
            })

        # Signal detected if 3+ cases
        signal_detected = len(matches) >= 3

        return APIResponse(
            status_code=200,
            data={
                "signal_detected": signal_detected,
                "case_count": len(matches),
                "matching_cases": matches,
                "lookback_days": lookback_days,
                "product": product_name,
                "ae_term": ae_term
            }
        )


# Utility functions
def compute_sha256(content: str) -> str:
    """Compute SHA-256 hash of content"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def generate_source_document(filename: str, content: str, received_at: str) -> Dict[str, Any]:
    """
    Generate SourceDocument metadata for FDA Requirement 1.
    """
    # Infer format from filename
    format_map = {
        ".txt": "TEXT",
        ".json": "JSON",
        ".vtt": "VTT",
        ".pdf": "PDF",
        ".eml": "EMAIL"
    }

    file_format = "TEXT"  # default
    for ext, fmt in format_map.items():
        if filename.lower().endswith(ext):
            file_format = fmt
            break

    return {
        "filename": filename,
        "format": file_format,
        "received_at": received_at,
        "sha256_hash": compute_sha256(content)
    }


class MockProductRSIDatabase:
    """
    Mock Product Reference Safety Information (RSI) database.
    Parses RSI markdown files from mock-data/product-information/ directory.
    Used for ADR-2 expectedness assessment.
    """

    def __init__(self, rsi_directory: str = "mock-data/product-information"):
        self.rsi_directory = rsi_directory
        self.rsi_cache: Dict[str, Dict[str, Any]] = {}
        self._load_rsi_files()

    def _load_rsi_files(self):
        """Load and parse RSI files from directory"""
        import os
        import re

        if not os.path.exists(self.rsi_directory):
            return

        for filename in os.listdir(self.rsi_directory):
            if filename.endswith("_RSI.md"):
                product_name = filename.replace("_RSI.md", "").lower()
                filepath = os.path.join(self.rsi_directory, filename)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Parse expected AE terms from RSI content
                    expected_terms = self._parse_expected_terms(content)

                    self.rsi_cache[product_name] = {
                        "filename": filename,
                        "expected_terms": expected_terms,
                        "content": content
                    }
                except Exception:
                    continue

    def _parse_expected_terms(self, content: str) -> List[str]:
        """
        Parse expected AE terms from RSI markdown content.
        Extracts terms from bulleted lists under "Common", "Uncommon", "Rare" sections ONLY.
        Excludes terms under "Not currently listed" or "Not listed" sections.
        """
        import re

        terms = []
        in_expected_section = False
        in_not_listed_section = False

        for line in content.split('\n'):
            line_stripped = line.strip()

            # Check if entering "Not currently listed" or "Not listed" section
            if line_stripped.startswith("**Not") or "not currently listed" in line_stripped.lower() or "not listed" in line_stripped.lower():
                in_not_listed_section = True
                in_expected_section = False
                continue

            # Check if entering expected sections
            if line_stripped.startswith("**Common") or line_stripped.startswith("**Uncommon") or line_stripped.startswith("**Rare"):
                in_expected_section = True
                in_not_listed_section = False
                continue

            # Check if leaving expected section (new ## heading)
            if line_stripped.startswith("##"):
                in_expected_section = False
                in_not_listed_section = False
                continue

            # Extract bullet points only if in expected section
            if in_expected_section and not in_not_listed_section:
                bullet_pattern = r'^- (.+)$'
                match = re.match(bullet_pattern, line_stripped)
                if match:
                    term_text = match.group(1)
                    # Clean up term (remove parenthetical notes)
                    term = re.sub(r'\s*\(.*?\)\s*', '', term_text).strip()
                    # Remove trailing punctuation
                    term = re.sub(r'[.,;]$', '', term).strip()
                    if term:
                        terms.append(term.lower())

        return terms

    def get_rsi(self, product_name: str) -> Optional[Dict[str, Any]]:
        """
        Get RSI data for a product.
        Returns: Dict with expected_terms list and content, or None if not found.
        """
        normalized_name = product_name.lower().strip()
        return self.rsi_cache.get(normalized_name)

    def is_expected(self, product_name: str, ae_term: str) -> bool:
        """
        Check if AE term is listed as expected in product RSI.
        Returns: True if term found in RSI expected terms, False otherwise.
        """
        rsi_data = self.get_rsi(product_name)
        if not rsi_data:
            return False

        normalized_term = ae_term.lower().strip()

        # Direct match
        if normalized_term in rsi_data["expected_terms"]:
            return True

        # Fuzzy match (substring)
        for expected_term in rsi_data["expected_terms"]:
            if normalized_term in expected_term or expected_term in normalized_term:
                return True

        return False

    def list_products(self) -> List[str]:
        """Return list of products with loaded RSI data"""
        return list(self.rsi_cache.keys())
