"""
Preprocessors for demo/claims_pipeline.ipynb

Simulates the IDP (Intelligent Document Processing) pipeline component of ADR-1.
Each preprocessor converts a raw claim file into the field-map + confidence-score
format that the ADR-1 LLM step receives as input.

In production this extraction is done by format-specific services (EDI parser,
OCR service, NLP extractor). The demo replaces those services with Python code
that produces equivalent structured output.

Supported formats:
  - portal JSON          (.json)   → PORTAL_JSON
  - FHIR R4              (.json)   → FHIR_R4
  - EDI 837P             (.edi)    → EDI_837P
  - EDI 837I             (.edi)    → EDI_837I
  - CMS-1500 OCR text    (.txt)    → CMS1500_OCR_TEXT
  - CMS-1500 paper PDF   (.pdf)    → CMS1500_PDF       (pdfplumber simulates OCR service)
  - email                (.eml)    → EMAIL
  - fax-email            (.txt)    → FAX_EMAIL
  - fax PDF              (.pdf)    → FAX               (pdfplumber simulates OCR service)
  - exception note       (.txt/.pdf) → EXCEPTION_NOTE
"""

import json
import re
from pathlib import Path


# ── Shared helpers ────────────────────────────────────────────────────────────

def _cf(value, conf):
    """Wrap a field value with its extraction confidence score."""
    return {"value": value, "confidence": conf}


def _find(pattern, text, flags=re.IGNORECASE):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


def _extract_text_from_pdf(path: str) -> str:
    """Extract text layer from a PDF using pdfplumber (simulates OCR service output)."""
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


# ── Portal JSON ───────────────────────────────────────────────────────────────

def preprocess_portal_json(path: str) -> dict:
    with open(path) as f:
        raw = json.load(f)

    pt    = raw.get("patient", {})
    ins   = raw.get("insurance", {})
    lines = raw.get("service_lines", [])

    icd10 = [d["code"] for d in raw.get("diagnoses", []) if d.get("code")]
    cpt   = list(dict.fromkeys(ln["cpt_code"] for ln in lines if ln.get("cpt_code")))

    dos_dates = [ln["date_of_service"] for ln in lines if ln.get("date_of_service")]
    dos_start = min(dos_dates) if dos_dates else None
    dos_end   = max(dos_dates) if dos_dates else None

    pos = lines[0].get("place_of_service") if lines else None

    pan = raw.get("prior_auth_number")
    prior_auth_required = pan is not None

    return {
        "source_format":    "PORTAL_JSON",
        "source_claim_ref": raw.get("submission_id", Path(path).stem),
        "intake_channel":   "PORTAL_JSON",
        "extracted_fields": {
            "member_id":               _cf(ins.get("member_id"),                   0.99),
            "member_name_last":        _cf(pt.get("last_name"),                    0.97),
            "member_name_first":       _cf(pt.get("first_name"),                   0.97),
            "member_dob":              _cf(pt.get("date_of_birth"),                0.98),
            "payer_id":                _cf(ins.get("payer_id"),                    0.99),
            "payer_name":              _cf(ins.get("payer_name"),                  0.99),
            "plan_id":                 _cf(ins.get("group_id"),                    0.95),
            "date_of_service_start":   _cf(dos_start,                             0.97),
            "date_of_service_end":     _cf(dos_end,                               0.97),
            "place_of_service_code":   _cf(pos,                                   0.99),
            "claim_type":              _cf("PROFESSIONAL",                        0.97),
            "icd10_codes":             _cf(icd10,                                 0.96),
            "cpt_codes":               _cf(cpt,                                   0.96),
            "billed_amount":           _cf(raw.get("total_charge_amount"),        0.99),
            "prior_auth_required":     _cf(prior_auth_required,                   0.97),
            "prior_auth_number":       _cf(pan, 1.00 if pan is None else 0.95),
            "billing_provider_npi":    _cf(raw.get("submitter", {}).get("npi"),   0.99),
            "billing_provider_tax_id": _cf(raw.get("submitter", {}).get("tax_id"),0.98),
            "rendering_provider_npi":  _cf(None,                                  0.00),
        },
    }


# ── FHIR R4 ───────────────────────────────────────────────────────────────────

def preprocess_fhir_r4(path: str) -> dict:
    with open(path) as f:
        raw = json.load(f)

    # Identifiers
    source_claim_ref = raw.get("id", Path(path).stem)

    # Member ID — strip "Patient/" prefix from reference
    patient_ref = raw.get("patient", {}).get("reference", "")
    member_id = patient_ref.split("/")[-1] if "/" in patient_ref else (patient_ref or None)

    # Member name — "First Last" or "Last, First" from display
    patient_display = raw.get("patient", {}).get("display", "")
    member_last = member_first = None
    if patient_display:
        parts = patient_display.strip().split()
        if len(parts) >= 2:
            member_last  = parts[-1]
            member_first = parts[0]
        else:
            member_last = patient_display

    # Payer — strip "Organization/" prefix
    insurer     = raw.get("insurer", {})
    insurer_ref = insurer.get("reference", "")
    payer_id    = insurer_ref.split("/")[-1] if "/" in insurer_ref else (insurer_ref or None)
    payer_name  = insurer.get("display")

    # Billing provider NPI — strip "Practitioner/" prefix
    provider_ref = raw.get("provider", {}).get("reference", "")
    billing_npi  = provider_ref.split("/")[-1] if "/" in provider_ref else (provider_ref or None)

    # Dates of service from items
    items     = raw.get("item", [])
    dos_dates = [it["servicedDate"] for it in items if it.get("servicedDate")]
    dos_start = min(dos_dates) if dos_dates else raw.get("billablePeriod", {}).get("start")
    dos_end   = max(dos_dates) if dos_dates else raw.get("billablePeriod", {}).get("end")

    # Place of service — first item's location code
    pos = None
    if items:
        loc = items[0].get("locationCodeableConcept", {})
        coding = loc.get("coding", [])
        pos = coding[0].get("code") if coding else None

    # ICD-10 codes
    icd10_codes = []
    for dx in raw.get("diagnosis", []):
        for coding in dx.get("diagnosisCodeableConcept", {}).get("coding", []):
            code = coding.get("code")
            if code:
                icd10_codes.append(code)

    # CPT codes
    cpt_codes = []
    billed_items = []
    for it in items:
        for coding in it.get("productOrService", {}).get("coding", []):
            code = coding.get("code")
            if code:
                cpt_codes.append(code)
        net = it.get("net", {}).get("value") or it.get("unitPrice", {}).get("value")
        if net:
            billed_items.append(net)

    cpt_codes = list(dict.fromkeys(cpt_codes))

    # Billed amount — prefer total field
    total_obj     = raw.get("total", {})
    billed_amount = total_obj.get("value") if total_obj else (sum(billed_items) if billed_items else None)

    # Claim type
    type_codings = raw.get("type", {}).get("coding", [])
    claim_type_code = type_codings[0].get("code", "professional").upper() if type_codings else "PROFESSIONAL"

    # Prior auth — look in supportingInfo
    prior_auth_number = None
    for si in raw.get("supportingInfo", []):
        cat = si.get("category", {}).get("coding", [{}])[0].get("code", "")
        if "auth" in cat.lower():
            prior_auth_number = si.get("valueString") or si.get("valueIdentifier", {}).get("value")
    prior_auth_required = prior_auth_number is not None

    return {
        "source_format":    "FHIR_R4",
        "source_claim_ref": source_claim_ref,
        "intake_channel":   "FHIR_R4",
        "extracted_fields": {
            "member_id":               _cf(member_id,          0.97 if member_id else 0.0),
            "member_name_last":        _cf(member_last,        0.90 if member_last else 0.0),
            "member_name_first":       _cf(member_first,       0.90 if member_first else 0.0),
            "member_dob":              _cf(None,               0.00),  # not in Claim resource
            "payer_id":                _cf(payer_id,           0.97 if payer_id else 0.0),
            "payer_name":              _cf(payer_name,         0.97 if payer_name else 0.0),
            "plan_id":                 _cf(None,               0.00),  # not in this Claim resource
            "date_of_service_start":   _cf(dos_start,         0.98 if dos_start else 0.0),
            "date_of_service_end":     _cf(dos_end,           0.98 if dos_end else 0.0),
            "place_of_service_code":   _cf(pos,               0.97 if pos else 0.0),
            "claim_type":              _cf(claim_type_code,   0.97),
            "icd10_codes":             _cf(icd10_codes,       0.98 if icd10_codes else 0.0),
            "cpt_codes":               _cf(cpt_codes,         0.98 if cpt_codes else 0.0),
            "billed_amount":           _cf(billed_amount,     0.98 if billed_amount else 0.0),
            "prior_auth_required":     _cf(prior_auth_required, 0.90),
            "prior_auth_number":       _cf(prior_auth_number, 0.95 if prior_auth_number else 1.0),
            "billing_provider_npi":    _cf(billing_npi,       0.96 if billing_npi else 0.0),
            "billing_provider_tax_id": _cf(None,              0.00),  # not in Claim resource
            "rendering_provider_npi":  _cf(None,              0.00),
        },
    }


# ── EDI 837P / 837I ───────────────────────────────────────────────────────────

def _edi_segments(text: str) -> list:
    text = text.replace("\n", "").replace("\r", "")
    return [seg.strip().split("*") for seg in text.split("~") if seg.strip()]


def _el(seg, idx, default=None):
    try:
        v = seg[idx]
        return v if v.strip() else default
    except IndexError:
        return default


def _icd10_dot(code: str) -> str:
    code = code.strip()
    if not code or "." in code:
        return code
    return (code[:3] + "." + code[3:]) if len(code) > 3 else code


def preprocess_edi(path: str) -> dict:
    """Auto-detect EDI 837P vs 837I from the transaction set identifier, then parse."""
    with open(path) as f:
        text = f.read()

    segs = _edi_segments(text)

    # Detect transaction type from ST segment (element 3 = implementation convention)
    is_837i = any(
        s[0] == "ST" and len(s) > 3 and "X223" in s[3]
        for s in segs
    )

    format_name = "EDI_837I" if is_837i else "EDI_837P"
    claim_type  = "INSTITUTIONAL" if is_837i else "PROFESSIONAL"

    by_tag: dict = {}
    for s in segs:
        by_tag.setdefault(s[0], []).append(s)

    # Claim reference + billed amount + place of service
    clm = (by_tag.get("CLM") or [[]])[0]
    source_claim_ref = _el(clm, 1)
    billed_amount    = float(_el(clm, 2, 0) or 0)
    pos_composite    = _el(clm, 5, "")
    place_of_service = pos_composite.split(":")[0] if pos_composite else None

    # Member — NM1*IL
    member_id = member_last = member_first = None
    for nm in by_tag.get("NM1", []):
        if _el(nm, 1) == "IL":
            member_last  = _el(nm, 3)
            member_first = _el(nm, 4)
            member_id    = _el(nm, 9)

    # Payer — NM1*PR or NM1*40
    payer_name = payer_id = None
    for nm in by_tag.get("NM1", []):
        if _el(nm, 1) in ("PR", "40"):
            payer_name = _el(nm, 3)
            payer_id   = _el(nm, 9)

    # Billing provider NPI — NM1*85
    billing_npi = None
    for nm in by_tag.get("NM1", []):
        if _el(nm, 1) == "85":
            billing_npi = _el(nm, 9)

    # Billing provider tax ID — REF*EI
    billing_tax = None
    for ref in by_tag.get("REF", []):
        if _el(ref, 1) == "EI":
            billing_tax = _el(ref, 2)

    # Date of birth — DMG
    dmg = (by_tag.get("DMG") or [[]])[0]
    dob_raw    = _el(dmg, 2)
    member_dob = (f"{dob_raw[:4]}-{dob_raw[4:6]}-{dob_raw[6:]}"
                  if dob_raw and len(dob_raw) == 8 else None)

    # ICD-10 codes — HI segments
    icd10_codes = []
    for hi in by_tag.get("HI", []):
        for el in hi[1:]:
            if el and ":" in el:
                qual, code = el.split(":", 1)
                if qual in ("ABK", "ABF", "BK", "BF"):
                    code_val = _icd10_dot(code)
                    if code_val:
                        icd10_codes.append(code_val)

    # CPT/procedure codes + dates of service
    # 837P uses SV1; 837I uses SV2 (but some 837I claims also carry SV1 lines)
    cpt_codes = []
    dos_dates  = []
    for seg in segs:
        tag = seg[0]
        if tag == "SV1":
            composite = _el(seg, 1, "")
            parts = composite.split(":")
            if len(parts) >= 2 and parts[1].strip():
                cpt_codes.append(parts[1].strip())
        elif tag == "SV2":
            # SV2*revenue_code*HC:cpt_code*charge...
            composite = _el(seg, 2, "")
            parts = composite.split(":")
            if len(parts) >= 2 and parts[1].strip():
                cpt_codes.append(parts[1].strip())
        elif tag == "DTP" and _el(seg, 1) == "472":
            raw_date = _el(seg, 3, "")
            if len(raw_date) == 8:
                dos_dates.append(f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}")

    dos_start = min(dos_dates) if dos_dates else None
    dos_end   = max(dos_dates) if dos_dates else None

    # Prior auth — REF*G1
    prior_auth_number = None
    for ref in by_tag.get("REF", []):
        if _el(ref, 1) == "G1":
            prior_auth_number = _el(ref, 2)
    prior_auth_required = prior_auth_number is not None

    # Plan/group — SBR
    plan_id = None
    for sbr in by_tag.get("SBR", []):
        plan_id = _el(sbr, 3) or None

    return {
        "source_format":    format_name,
        "source_claim_ref": source_claim_ref or Path(path).stem,
        "intake_channel":   format_name,
        "extracted_fields": {
            "member_id":               _cf(member_id, 1.0 if member_id else 0.0),
            "member_name_last":        _cf(member_last, 1.0 if member_last else 0.0),
            "member_name_first":       _cf(member_first, 1.0 if member_first else 0.0),
            "member_dob":              _cf(member_dob, 1.0 if member_dob else 0.0),
            "payer_id":                _cf(payer_id, 1.0 if payer_id else 0.0),
            "payer_name":              _cf(payer_name, 1.0 if payer_name else 0.0),
            "plan_id":                 _cf(plan_id, 1.0 if plan_id else 0.0),
            "date_of_service_start":   _cf(dos_start, 1.0 if dos_start else 0.0),
            "date_of_service_end":     _cf(dos_end, 1.0 if dos_end else 0.0),
            "place_of_service_code":   _cf(place_of_service, 1.0 if place_of_service else 0.0),
            "claim_type":              _cf(claim_type, 1.0),
            "icd10_codes":             _cf(icd10_codes, 1.0 if icd10_codes else 0.0),
            "cpt_codes":               _cf(list(dict.fromkeys(cpt_codes)), 1.0 if cpt_codes else 0.0),
            "billed_amount":           _cf(billed_amount, 1.0 if billed_amount else 0.0),
            "prior_auth_required":     _cf(prior_auth_required, 1.0),
            "prior_auth_number":       _cf(prior_auth_number, 1.0 if prior_auth_number else 1.0),
            "billing_provider_npi":    _cf(billing_npi, 1.0 if billing_npi else 0.0),
            "billing_provider_tax_id": _cf(billing_tax, 1.0 if billing_tax else 0.0),
            "rendering_provider_npi":  _cf(None, 0.0),
        },
    }


# Keep legacy name so any existing callers still work
preprocess_edi_837p = preprocess_edi


# ── CMS-1500 OCR text ─────────────────────────────────────────────────────────

def preprocess_cms1500_ocr(path: str) -> dict:
    with open(path) as f:
        text = f.read()
    return _parse_cms1500_text(text, Path(path).stem, "CMS1500_OCR_TEXT", ocr_noise=True)


# ── CMS-1500 paper PDF ────────────────────────────────────────────────────────
# In production a real OCR service processes the scanned paper form and returns
# extracted text. Here pdfplumber extracts the text layer from digitally-generated
# mock PDFs, producing equivalent output for the demo.

def preprocess_cms1500_pdf(path: str) -> dict:
    text = _extract_text_from_pdf(path)
    return _parse_cms1500_text(text, Path(path).stem, "CMS1500_PDF", ocr_noise=False)


def _parse_cms1500_text(text: str, stem: str, intake_channel: str, ocr_noise: bool) -> dict:
    """
    Field extraction for CMS-1500 form content, shared between OCR text and paper PDF.
    ocr_noise=True uses lower confidence baselines to account for OCR artifacts.
    """
    base   = 0.80 if ocr_noise else 0.95   # baseline confidence
    thresh = 0.68 if ocr_noise else 0.88   # threshold for short/noisy values

    # Member ID — field 1a
    member_id_raw = _find(r"INSURED.{1,5}I\.?D\.?\s*NUMBER[:\s]+([A-Z0-9\-]+)", text)
    if not member_id_raw:
        member_id_raw = _find(r"1a\.?\s*Insured['\u2019]?s\s*ID[:\s]+([A-Z0-9\-]+)", text)

    # Patient name — field 2
    name_raw = _find(r"PATIENT.{1,5}NAME[^:]*:\s*([A-Za-z ]+)", text)
    if not name_raw:
        name_raw = _find(r"2\.?\s*Patient\s*Name[:\s]+([A-Za-z,\s]+?)(?:\n|$)", text)
    member_last = member_first = None
    if name_raw:
        parts = re.split(r"[,\s]{2,}", name_raw.strip(), maxsplit=1)
        if len(parts) == 1:
            parts = name_raw.strip().split()
        member_last  = parts[0].strip() if parts else None
        member_first = parts[1].strip() if len(parts) > 1 else None

    # DOB — field 3
    dob_raw = _find(r"BIRTH\s*DATE[:\s]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{4})", text)
    if not dob_raw:
        dob_raw = _find(r"3\.?\s*Patient\s*DOB[^:]*:\s*(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{4})", text)
    member_dob = None
    if dob_raw:
        parts = re.split(r"[\s/\-]+", dob_raw)
        if len(parts) == 3:
            member_dob = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"

    # Insurance plan / payer name — field 11c
    payer_name = _find(r"INSURANCE\s*PLAN\s*NAME[:\s]+([^\n]+)", text)
    if not payer_name:
        payer_name = _find(r"11c\.?\s*Insurance\s*Plan[:\s]+([^\n]+)", text)

    # Group number — field 11
    plan_id = _find(r"(?:POLICY|GROUP)\s*(?:GROUP\s*)?(?:NUMBER|#)[:\s]+([A-Z0-9\-]+)", text)
    if not plan_id:
        plan_id = _find(r"11\.?\s*Policy\s*Group\s*#[:\s]+([A-Z0-9\-]+)", text)

    # Tax ID — field 25
    tax_id = _find(r"FEDERAL\s*TAX\s*I\.?D\.?\s*[NM][^:]*[:\s]+([0-9\-]+)", text)
    if not tax_id:
        tax_id = _find(r"25\.?\s*Federal\s*Tax\s*ID[:\s]+([0-9\-]+)", text)

    # Billing provider NPI — field 33
    billing_npi = _find(r"(?:33\.|NPI)[:\s]+(\d{10})", text)

    # Claim ref — field 26 (patient account number)
    claim_ref_raw = _find(r"PATIENT.{1,5}ACCOUNT\s*NO\.?[:\s]+([A-Z][A-Z0-9 \-]+)", text)
    if not claim_ref_raw:
        claim_ref_raw = _find(r"26\.?\s*Patient\s*Account\s*#[:\s]+([A-Z0-9\-]+)", text)
    claim_ref = re.sub(r"\s+", "", claim_ref_raw).strip("-") if claim_ref_raw else None
    if claim_ref and len(claim_ref) < 5:
        claim_ref = None

    # ICD-10 codes — field 21
    icd10_raw   = re.findall(r"\b([A-Z]\d{2}(?:\.\d+)?)\b", text)
    icd10_codes = list(dict.fromkeys(icd10_raw)) if icd10_raw else []

    # Service lines — field 24: date | POS | CPT or date  POS  CPT
    svc_pipe    = re.findall(r"(\d{4}-\d{2}-\d{2})\s*\|\s*POS\s+(\d{2})\s*\|\s*CPT\s+(\d{4,5})", text)
    svc_space   = re.findall(r"(\d{4}-\d{2}-\d{2})\s+(\d{2})\s+([\d\s]{5,7})", text)
    service_matches = svc_pipe if svc_pipe else svc_space

    dos_dates  = []
    cpt_codes  = []
    pos_code   = None
    for match in service_matches:
        dos_dates.append(match[0])
        pos_code = match[1]
        cpt_raw  = match[2].replace(" ", "").strip()
        cpt_codes.append(cpt_raw)

    dos_start = min(dos_dates) if dos_dates else None
    dos_end   = max(dos_dates) if dos_dates else None

    # Total charge — field 28
    total_raw = _find(r"TOTAL\s*CHARGE[:\s\$]+([0-9,\.]+)", text)
    if not total_raw:
        total_raw = _find(r"28\.?\s*Total\s*Charge[:\s\$,]+([0-9,\.]+)", text)
    billed = float(total_raw.replace(",", "")) if total_raw else None

    # Confidence adjustments for OCR noise
    name_conf = thresh if (ocr_noise and member_last and len(member_last) <= 4) else base
    cpt_conf  = thresh if (ocr_noise and any(" " in c for c in cpt_codes)) else base

    return {
        "source_format":    intake_channel,
        "source_claim_ref": claim_ref or stem,
        "intake_channel":   intake_channel,
        "extracted_fields": {
            "member_id":               _cf(member_id_raw, base + 0.04 if member_id_raw else 0.0),
            "member_name_last":        _cf(member_last,   name_conf if member_last else 0.0),
            "member_name_first":       _cf(member_first,  name_conf if member_first else 0.0),
            "member_dob":              _cf(member_dob,    base + 0.04 if member_dob else 0.0),
            "payer_id":                _cf(None,          0.00),
            "payer_name":              _cf(payer_name,    base if payer_name else 0.0),
            "plan_id":                 _cf(plan_id,       base if plan_id else 0.0),
            "date_of_service_start":   _cf(dos_start,     base + 0.03 if dos_start else 0.0),
            "date_of_service_end":     _cf(dos_end,       base + 0.03 if dos_end else 0.0),
            "place_of_service_code":   _cf(pos_code,      base + 0.06 if pos_code else 0.0),
            "claim_type":              _cf("PROFESSIONAL", base + 0.04),
            "icd10_codes":             _cf(icd10_codes,   base + 0.01 if icd10_codes else 0.0),
            "cpt_codes":               _cf(cpt_codes,     cpt_conf if cpt_codes else 0.0),
            "billed_amount":           _cf(billed,        base + 0.05 if billed else 0.0),
            "prior_auth_required":     _cf(False,         base + 0.01),
            "prior_auth_number":       _cf(None,          1.00),
            "billing_provider_tax_id": _cf(tax_id,        base - 0.01 if tax_id else 0.0),
            "billing_provider_npi":    _cf(billing_npi,   base + 0.03 if billing_npi else 0.0),
            "rendering_provider_npi":  _cf(None,          0.00),
        },
    }


# ── Email body parser (shared by EMAIL and FAX_EMAIL) ────────────────────────

def _parse_email_body(body: str, intake_channel: str, source_ref_hint: str = None,
                      header_npi: str = None, header_tax_id: str = None) -> dict:
    """Extract claim fields from a plain-text email body."""

    # Patient name — "Patient: Last, First" or "Patient: First Last (DOB ...)"
    name_raw = _find(r"Patient[:\s]+([A-Za-z,\s]+?)(?:\s*\(|$)", body)
    member_last = member_first = None
    if name_raw:
        parts = re.split(r",\s*", name_raw.strip(), maxsplit=1)
        if len(parts) == 1:
            parts = name_raw.strip().split()
        member_last  = parts[0].strip() if parts else None
        member_first = parts[1].strip() if len(parts) > 1 else None

    # DOB — "(DOB YYYY-MM-DD, ...)" or "DOB: YYYY-MM-DD"
    dob_raw    = _find(r"\(DOB\s+(\d{4}-\d{2}-\d{2})", body)
    if not dob_raw:
        dob_raw = _find(r"DOB[:\s]+(\d{4}-\d{2}-\d{2})", body)
    member_dob = dob_raw

    # Member ID
    member_id = _find(r"Member\s*ID[:\s]+([A-Z0-9\-]+)", body)

    # Plan / payer name
    plan_raw   = _find(r"Plan[:\s]+([^\n]+)", body)
    payer_name = plan_raw.strip() if plan_raw else None

    # Group / plan ID
    group_raw = _find(r"Group[:\s]+([A-Z0-9\-]+)", body)
    plan_id   = group_raw.strip() if group_raw else None

    # Claim reference
    claim_ref = _find(r"[Cc]laim\s*(?:reference|ref(?:erence)?|id|#)?[:\s]+([A-Z0-9\-]+)", body)
    if not claim_ref:
        claim_ref = source_ref_hint

    # NPI and Tax ID — prefer X-header values; fall back to body
    billing_npi = header_npi or _find(r"\bNPI[:\s]+(\d{10})\b", body)
    tax_id      = header_tax_id or _find(r"Tax\s*ID[:\s]+([\d\-]+)", body)

    # ICD-10 codes
    icd10_raw   = re.findall(r"\b([A-Z]\d{2}(?:\.\d+)?)\b", body)
    icd10_codes = list(dict.fromkeys(icd10_raw)) if icd10_raw else []

    # Service lines — "YYYY-MM-DD: CPT XXXXX (...)"
    svc_matches = re.findall(r"(\d{4}-\d{2}-\d{2}):\s+CPT\s+(\d{4,5})", body)
    dos_dates   = [m[0] for m in svc_matches]
    cpt_codes   = list(dict.fromkeys(m[1] for m in svc_matches))

    dos_start = min(dos_dates) if dos_dates else None
    dos_end   = max(dos_dates) if dos_dates else None

    # Total charge
    total_raw = _find(r"Total[:\s\$]+([0-9,\.]+)", body)
    billed    = float(total_raw.replace(",", "")) if total_raw else None

    return {
        "source_claim_ref": claim_ref or source_ref_hint,
        "intake_channel":   intake_channel,
        "extracted_fields": {
            "member_id":               _cf(member_id,    0.91 if member_id else 0.0),
            "member_name_last":        _cf(member_last,  0.88 if member_last else 0.0),
            "member_name_first":       _cf(member_first, 0.88 if member_first else 0.0),
            "member_dob":              _cf(member_dob,   0.91 if member_dob else 0.0),
            "payer_id":                _cf(None,         0.00),
            "payer_name":              _cf(payer_name,   0.84 if payer_name else 0.0),
            "plan_id":                 _cf(plan_id,      0.88 if plan_id else 0.0),
            "date_of_service_start":   _cf(dos_start,    0.90 if dos_start else 0.0),
            "date_of_service_end":     _cf(dos_end,      0.90 if dos_end else 0.0),
            "place_of_service_code":   _cf(None,         0.00),
            "claim_type":              _cf("PROFESSIONAL", 0.85),
            "icd10_codes":             _cf(icd10_codes,  0.87 if icd10_codes else 0.0),
            "cpt_codes":               _cf(cpt_codes,    0.87 if cpt_codes else 0.0),
            "billed_amount":           _cf(billed,       0.90 if billed else 0.0),
            "prior_auth_required":     _cf(False,        0.75),
            "prior_auth_number":       _cf(None,         1.00),
            "billing_provider_npi":    _cf(billing_npi,  0.93 if billing_npi else 0.0),
            "billing_provider_tax_id": _cf(tax_id,       0.90 if tax_id else 0.0),
            "rendering_provider_npi":  _cf(None,         0.00),
        },
    }


# ── Email (.eml) ─────────────────────────────────────────────────────────────

def preprocess_email(path: str) -> dict:
    import email as email_lib
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = email_lib.message_from_file(f)

    # High-reliability fields from X-headers
    header_npi    = raw.get("X-Submitter-NPI")
    header_tax_id = raw.get("X-Submitter-TaxID")

    # Decode quoted-printable / base64 body
    body = ""
    if raw.is_multipart():
        for part in raw.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                break
    else:
        payload = raw.get_payload(decode=True)
        body = payload.decode("utf-8", errors="replace") if payload else raw.get_payload()

    stem   = Path(path).stem
    parsed = _parse_email_body(body, "EMAIL", stem, header_npi, header_tax_id)

    return {
        "source_format":    "EMAIL",
        "source_claim_ref": parsed["source_claim_ref"] or stem,
        "intake_channel":   "EMAIL",
        "extracted_fields": parsed["extracted_fields"],
    }


# ── Fax-email (.txt) ─────────────────────────────────────────────────────────

def preprocess_fax_email(path: str) -> dict:
    import email as email_lib
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = email_lib.message_from_file(f)

    body   = raw.get_payload() if not raw.is_multipart() else ""
    stem   = Path(path).stem
    parsed = _parse_email_body(body or "", "FAX_EMAIL", stem)

    return {
        "source_format":    "FAX_EMAIL",
        "source_claim_ref": parsed["source_claim_ref"] or stem,
        "intake_channel":   "FAX_EMAIL",
        "extracted_fields": parsed["extracted_fields"],
    }


# ── Fax PDF ───────────────────────────────────────────────────────────────────
# In production a fax arrives as an image-based PDF; an OCR service extracts the text.
# The mock fax PDFs are digitally generated, so pdfplumber extracts equivalent text.

def preprocess_fax_pdf(path: str) -> dict:
    text = _extract_text_from_pdf(path)
    stem = Path(path).stem

    # Patient name — "RE: Claim submission — patient Last, First"
    name_raw = _find(r"RE:.*patient\s+([A-Za-z]+,?\s+[A-Za-z]+)", text)
    member_last = member_first = None
    if name_raw:
        parts = re.split(r",\s*", name_raw.strip(), maxsplit=1)
        if len(parts) == 1:
            parts = name_raw.strip().split()
        member_last  = parts[0].strip() if parts else None
        member_first = parts[1].strip() if len(parts) > 1 else None

    # Member fields
    member_id  = _find(r"Member\s*ID[:\s]+([A-Z0-9\-]+)", text)
    dob_raw    = _find(r"Patient\s*DOB[:\s]+(\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{4})", text)
    member_dob = None
    if dob_raw:
        parts = re.split(r"[\s/\-]+", dob_raw)
        if len(parts) == 3:
            member_dob = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"

    # Plan / group
    plan_raw  = _find(r"Plan[:\s]+([^\n]+)", text)
    payer_name = plan_raw.strip() if plan_raw else None
    group_raw  = _find(r"Group\s*#?[:\s]+([A-Z0-9\-]+)", text)
    plan_id    = group_raw.strip() if group_raw else None

    # Provider
    billing_npi = _find(r"Provider\s*NPI[:\s]+(\d{10})", text)
    tax_id      = _find(r"Tax\s*ID[:\s]+([\d\-]+)", text)

    # Date of service
    dos_raw   = _find(r"Date\s*of\s*service[:\s]+(\d{4}-\d{2}-\d{2})", text)
    dos_start = dos_end = dos_raw

    # Diagnoses — comma-separated ICD-10 on one line
    dx_line  = _find(r"Diagnoses?[:\s]+([A-Z0-9\.,\s]+)", text)
    icd10_codes = []
    if dx_line:
        icd10_codes = [c.strip() for c in re.split(r"[,\s]+", dx_line) if re.match(r"[A-Z]\d{2}", c.strip())]

    # Procedures — comma-separated CPT codes
    proc_line = _find(r"Procedures?[:\s]+([\d\s,]+)", text)
    cpt_codes = []
    if proc_line:
        cpt_codes = [c.strip() for c in re.split(r"[,\s]+", proc_line) if re.match(r"\d{4,5}$", c.strip())]

    # Total charge
    total_raw = _find(r"Total\s*charge[:\s\$]+([0-9,\.]+)", text)
    billed    = float(total_raw.replace(",", "")) if total_raw else None

    return {
        "source_format":    "FAX",
        "source_claim_ref": stem,
        "intake_channel":   "FAX",
        "extracted_fields": {
            "member_id":               _cf(member_id,    0.87 if member_id else 0.0),
            "member_name_last":        _cf(member_last,  0.82 if member_last else 0.0),
            "member_name_first":       _cf(member_first, 0.82 if member_first else 0.0),
            "member_dob":              _cf(member_dob,   0.88 if member_dob else 0.0),
            "payer_id":                _cf(None,         0.00),
            "payer_name":              _cf(payer_name,   0.80 if payer_name else 0.0),
            "plan_id":                 _cf(plan_id,      0.85 if plan_id else 0.0),
            "date_of_service_start":   _cf(dos_start,    0.88 if dos_start else 0.0),
            "date_of_service_end":     _cf(dos_end,      0.88 if dos_end else 0.0),
            "place_of_service_code":   _cf(None,         0.00),
            "claim_type":              _cf("PROFESSIONAL", 0.82),
            "icd10_codes":             _cf(icd10_codes,  0.85 if icd10_codes else 0.0),
            "cpt_codes":               _cf(cpt_codes,    0.83 if cpt_codes else 0.0),
            "billed_amount":           _cf(billed,       0.87 if billed else 0.0),
            "prior_auth_required":     _cf(False,        0.72),
            "prior_auth_number":       _cf(None,         1.00),
            "billing_provider_npi":    _cf(billing_npi,  0.91 if billing_npi else 0.0),
            "billing_provider_tax_id": _cf(tax_id,       0.88 if tax_id else 0.0),
            "rendering_provider_npi":  _cf(None,         0.00),
        },
    }


# ── Exception note ────────────────────────────────────────────────────────────
# Exception notes are NOT claim submissions — they annotate an existing CMS record.
# The preprocessor extracts the referenced claim_id and any available identity fields.
# ADR-1 outputs routing_action (ANNOTATE_CLAIM or EXCEPTION_QUEUE), not extraction_status.

def preprocess_exception_note(path: str, text: str = None) -> dict:
    if text is None:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()

    stem = Path(path).stem

    # Claim reference the note is about
    claim_ref = _find(r"claim\s+([A-Z][A-Z0-9\-]+)", text, re.IGNORECASE)
    if not claim_ref:
        claim_ref = _find(r"([A-Z]{2,4}-\d{4}-\d{6,})", text)

    # Member ID — standalone alphanumeric that looks like an ID
    member_id = _find(r"\b([A-Z][A-Z0-9]{6,12})\b", text)

    return {
        "source_format":    "EXCEPTION_NOTE",
        "source_claim_ref": claim_ref or stem,
        "intake_channel":   "EXCEPTION_NOTE",
        "extracted_fields": {
            "claim_id_reference": claim_ref,
            "member_id":          member_id,
            "annotation_text":    text.strip(),
        },
    }


def preprocess_exception_note_pdf(path: str) -> dict:
    text = _extract_text_from_pdf(path)
    return preprocess_exception_note(path, text)


# ── Auto-detect dispatcher ────────────────────────────────────────────────────

def preprocess(path: str) -> dict:
    """
    Detect file format from extension and parent directory, then run the
    appropriate IDP preprocessor.
    """
    p      = Path(path)
    ext    = p.suffix.lower()
    parent = p.parent.name.lower()   # folder name used to disambiguate same-extension formats

    if ext == ".json":
        with open(path) as f:
            data = json.load(f)
        if data.get("resourceType") == "Claim":
            return preprocess_fhir_r4(path)
        return preprocess_portal_json(path)

    elif ext == ".edi":
        return preprocess_edi(path)

    elif ext == ".eml":
        return preprocess_email(path)

    elif ext == ".pdf":
        if "exception" in parent:
            return preprocess_exception_note_pdf(path)
        elif parent == "fax":
            return preprocess_fax_pdf(path)
        else:
            # cms1500-paper and any other PDF default to CMS-1500 form parser
            return preprocess_cms1500_pdf(path)

    elif ext == ".txt":
        if "fax-email" in parent or "fax_email" in parent:
            return preprocess_fax_email(path)
        elif "exception" in parent:
            return preprocess_exception_note(path)
        else:
            return preprocess_cms1500_ocr(path)

    else:
        raise ValueError(
            f"Unsupported file format: {ext!r} (folder: {parent!r}). "
            f"Supported: .json, .edi, .eml, .pdf, .txt"
        )
