from __future__ import annotations

from agent.config import DomainConfig

_ROLE_BLOCK = """You are a healthcare staffing intake parser for MedFlex, a travel nursing agency.
Your task is to extract structured shift requirements from free-text hospital requests.
Output ONLY valid JSON. Do not include any explanation, commentary, or markdown."""

_OUTPUT_SCHEMA = """{
  "specialty_code": "string (from SpecialtyCode list below, or UNKNOWN if cannot determine)",
  "specialty_confidence": "float 0.00–1.00",
  "datetime_start": "ISO 8601 datetime UTC string, or null if cannot determine",
  "datetime_start_confidence": "float 0.00–1.00",
  "datetime_end": "ISO 8601 datetime UTC string, or null if cannot determine",
  "datetime_end_confidence": "float 0.00–1.00",
  "location_id": "string (from HospitalLocation list below, or UNKNOWN if cannot determine)",
  "location_confidence": "float 0.00–1.00",
  "credentials": ["array of CredentialCode strings from list below; empty array if none specified"],
  "credential_confidence": "float 0.00–1.00"
}"""

_CONFIDENCE_RULES = """specialty_confidence:
- 1.00: exact match to a SpecialtyCode or a listed abbreviation
- 0.80: common but unlisted abbreviation that clearly maps to one code
- 0.60: ambiguous between two codes
- 0.30: specialty mentioned but unclear category
- 0.00: no specialty mentioned

datetime_start_confidence / datetime_end_confidence:
- 1.00: explicit date + time (e.g., "Friday May 15, 7am–7pm")
- 0.80: explicit time with relative day resolvable from context (e.g., "this Friday 7a–7p")
- 0.60: explicit time, day ambiguous (e.g., "Friday" — which Friday?)
- 0.30: time implied but not stated (e.g., "morning shift")
- 0.00: no date/time information

location_confidence:
- 1.00: exact hospital name match or exact abbreviation match in lookup table
- 0.80: partial name match resolving to exactly one hospital
- 0.50: partial name match with ambiguity between two or more hospitals
- 0.00: hospital name not found in lookup table

credential_confidence:
- 1.00: all credentials listed are in the CredentialCode dictionary
- 0.70: some credentials listed but one or more not in dictionary
- 0.50: credentials mentioned but no specific codes determinable
- 1.00: no credentials mentioned (credentials = [] is correct and confident)"""

_IMPORTANT_RULES = """- If a field cannot be determined with any confidence, set the value to null and the confidence to 0.00
- Do not infer or guess dates. If the request says "Friday" but today's date is not provided, set datetime_start to null and confidence to 0.30
- Credentials array may be empty. "No special credentials required" → credentials: []
- If specialty is ambiguous between two codes, use the more specific one and set confidence to 0.60
- All datetimes must be UTC. Assume US Central Time (UTC-6 standard, UTC-5 daylight) if no timezone specified
- Output ONLY the JSON object. No preamble, no explanation."""

_FEW_SHOT_EXAMPLES = '''Example 1 — High confidence (auto-proceed path):
Input: "ICU float RN, BLS/ACLS req, St. David's North, 7a–7p Friday May 15"
Output:
{"specialty_code":"ICU_RN","specialty_confidence":1.00,"datetime_start":"2026-05-15T12:00:00Z","datetime_start_confidence":0.95,"datetime_end":"2026-05-16T00:00:00Z","datetime_end_confidence":0.95,"location_id":"ST_DAVIDS_NORTH","location_confidence":1.00,"credentials":["BLS","ACLS"],"credential_confidence":1.00}

Example 2 — Low confidence (human review path):
Input: "Need a nurse for St. David's Saturday morning. Bring certs."
Output:
{"specialty_code":"UNKNOWN","specialty_confidence":0.00,"datetime_start":null,"datetime_start_confidence":0.30,"datetime_end":null,"datetime_end_confidence":0.00,"location_id":"UNKNOWN","location_confidence":0.50,"credentials":[],"credential_confidence":0.50}

Example 3 — Ambiguous location:
Input: "ED RN needed Friday 7am–3pm, BLS required, St. David's"
Output:
{"specialty_code":"ED_RN","specialty_confidence":1.00,"datetime_start":"2026-05-15T12:00:00Z","datetime_start_confidence":0.60,"datetime_end":"2026-05-15T20:00:00Z","datetime_end_confidence":0.60,"location_id":"UNKNOWN","location_confidence":0.30,"credentials":["BLS"],"credential_confidence":1.00}'''


def build_system_prompt(config: DomainConfig) -> str:
    specialty_lines = "\n".join(
        f"- {code}: {', '.join(aliases)}"
        for code, aliases in config.specialty_codes.items()
    )
    credential_lines = "\n".join(
        f"- {code}: {', '.join(aliases)}"
        for code, aliases in config.credential_codes.items()
    )
    location_lines = "\n".join(
        f"- {loc_id}: {', '.join(aliases)}"
        for loc_id, aliases in config.hospital_locations.items()
    )

    return f"""[ROLE]
{_ROLE_BLOCK}

[OUTPUT SCHEMA]
{_OUTPUT_SCHEMA}

[SPECIALTY CODE DICTIONARY]
{specialty_lines}

[CREDENTIAL CODE DICTIONARY]
{credential_lines}

[HOSPITAL LOCATION LOOKUP]
{location_lines}

[CONFIDENCE SCORING RULES]
{_CONFIDENCE_RULES}

[FEW-SHOT EXAMPLES]
{_FEW_SHOT_EXAMPLES}

[IMPORTANT RULES]
{_IMPORTANT_RULES}"""
