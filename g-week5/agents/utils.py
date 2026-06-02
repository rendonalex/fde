"""
Utility functions for ADR agents.
Includes confidence scoring, span citation generation, date parsing helpers.
"""

import re
from datetime import datetime, timedelta
from typing import Tuple, Optional


def estimate_confidence_from_context(
    extracted_value: str,
    source_text: str,
    has_explicit_label: bool = False,
    is_ambiguous: bool = False
) -> float:
    """
    Estimate extraction confidence based on contextual signals.

    High confidence (0.85-0.95):
    - Explicit field labels present ("Patient:", "Suspect Drug:")
    - Unambiguous structured data

    Medium confidence (0.70-0.84):
    - Implicit extraction from narrative text
    - Some ambiguity but reasonable inference

    Low confidence (0.50-0.69):
    - Highly ambiguous or conflicting information
    - Estimated/inferred values
    """

    base_confidence = 0.75

    # Boost for explicit labels
    if has_explicit_label:
        base_confidence += 0.15

    # Penalty for ambiguity
    if is_ambiguous:
        base_confidence -= 0.15

    # Boost for structured formats (JSON, clear formatting)
    if "{" in source_text or ":" in source_text:
        base_confidence += 0.05

    # Ensure within bounds
    return max(0.5, min(0.95, base_confidence))


def find_span_in_text(value: str, source_text: str, start_search: int = 0) -> Optional[Tuple[int, int]]:
    """
    Find character span of value in source text.
    Returns: (start_index, end_index) or None if not found.
    """
    # Normalize for search
    search_value = value.strip()

    # Try exact match first
    start_idx = source_text.find(search_value, start_search)
    if start_idx != -1:
        return (start_idx, start_idx + len(search_value))

    # Try case-insensitive match
    lower_text = source_text.lower()
    lower_value = search_value.lower()
    start_idx = lower_text.find(lower_value, start_search)
    if start_idx != -1:
        return (start_idx, start_idx + len(search_value))

    # Try fuzzy match (partial match, first occurrence)
    words = search_value.split()
    if len(words) > 2:
        # Try first few words
        partial = " ".join(words[:3])
        start_idx = source_text.find(partial, start_search)
        if start_idx != -1:
            return (start_idx, start_idx + len(partial))

    # Not found
    return None


def parse_ambiguous_date(date_str: str, received_at: datetime) -> Tuple[Optional[str], bool]:
    """
    Parse ambiguous date strings like "a few weeks ago", "last month".
    Returns: (ISO date string, is_estimated)
    """
    date_str_lower = date_str.lower().strip()
    estimated = False
    result_date = None

    # Pattern matching for relative dates
    if "week" in date_str_lower:
        # "a few weeks ago", "3 weeks ago"
        weeks_match = re.search(r'(\d+)\s*weeks?', date_str_lower)
        if weeks_match:
            weeks = int(weeks_match.group(1))
        else:
            # "a few weeks" -> assume 3 weeks
            weeks = 3
        result_date = received_at - timedelta(weeks=weeks)
        estimated = True

    elif "month" in date_str_lower:
        # "last month", "2 months ago"
        months_match = re.search(r'(\d+)\s*months?', date_str_lower)
        if months_match:
            months = int(months_match.group(1))
        else:
            months = 1
        result_date = received_at - timedelta(days=30 * months)
        estimated = True

    elif "day" in date_str_lower:
        # "5 days ago"
        days_match = re.search(r'(\d+)\s*days?', date_str_lower)
        if days_match:
            days = int(days_match.group(1))
            result_date = received_at - timedelta(days=days)
            estimated = True

    elif "yesterday" in date_str_lower:
        result_date = received_at - timedelta(days=1)
        estimated = True

    elif "today" in date_str_lower:
        result_date = received_at
        estimated = False

    # Try parsing as ISO date
    else:
        try:
            # Try various date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    result_date = parsed
                    estimated = False
                    break
                except ValueError:
                    continue
        except Exception:
            pass

    if result_date:
        return (result_date.strftime("%Y-%m-%d"), estimated)

    return (None, False)


def validate_date_consistency(
    drug_start: Optional[str],
    ae_onset: Optional[str],
    outcome_date: Optional[str]
) -> bool:
    """
    Validate temporal consistency: drug_start <= ae_onset <= outcome_date
    Returns: True if consistent or if dates missing
    """
    try:
        if drug_start and ae_onset:
            if drug_start > ae_onset:
                return False

        if ae_onset and outcome_date:
            if ae_onset > outcome_date:
                return False

        return True
    except Exception:
        return True  # Allow if unparseable


def classify_report_format(filename: str, content: str) -> str:
    """
    Classify report format based on filename and content structure.
    Returns: ReportFormat enum value as string.
    """
    filename_lower = filename.lower()

    if ".json" in filename_lower:
        if "webform" in filename_lower or "patient" in filename_lower:
            return "PATIENT_WEBFORM"
        elif "socmedia" in filename_lower or "social" in filename_lower:
            return "SOCIAL_MEDIA"
        else:
            return "PATIENT_WEBFORM"  # default JSON

    elif ".vtt" in filename_lower:
        return "PHONE_VTT"

    elif "hcp" in filename_lower:
        return "HCP_TEXT"

    elif "trial" in filename_lower or "site" in filename_lower:
        return "TRIAL_REPORT"

    elif "literature" in filename_lower:
        return "LITERATURE"

    else:
        # Analyze content structure
        if content.strip().startswith("{"):
            return "PATIENT_WEBFORM"
        elif "WEBVTT" in content or "-->":
            return "PHONE_VTT"
        else:
            return "HCP_TEXT"  # default text


def extract_received_timestamp(content: str, filename: str) -> str:
    """
    Extract received_at timestamp from content or filename.
    Returns: ISO 8601 timestamp string.
    """
    # Try to find timestamp in content
    timestamp_patterns = [
        r'receipt timestamp[:\s]+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})',
        r'received_at["\s:]+(\d{4}-\d{2}-\d{2}T[\d:]+)',
        r'(\d{4}-\d{2}-\d{2}T[\d:]+[-+]\d{2}:\d{2})'
    ]

    for pattern in timestamp_patterns:
        match = re.search(pattern, content)
        if match:
            timestamp_str = match.group(1)
            try:
                # Try parsing and converting to ISO format
                dt = datetime.fromisoformat(timestamp_str.replace(" ", "T"))
                return dt.isoformat() + "Z"
            except Exception:
                pass

    # Try extracting date from filename
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        date_str = date_match.group(1)
        # Use noon UTC as default time
        return f"{date_str}T12:00:00Z"

    # Fallback: use current timestamp
    return datetime.utcnow().isoformat() + "Z"


def normalize_product_name(drug_name: str) -> Optional[str]:
    """
    Normalize drug name to marketed product (Solivian, Tezarimab, Phaedora).
    Returns: Normalized product name or None if out-of-scope.
    """
    drug_lower = drug_name.lower().strip()

    # Product mapping (brand and generic names)
    product_map = {
        "tezarimab": "Tezarimab",
        "solivian": "Solivian",
        "solivimab": "Solivian",
        "phaedora": "Phaedora",
        "phaedexine": "Phaedora",
    }

    for key, product in product_map.items():
        if key in drug_lower:
            return product

    return None  # Out-of-scope product
