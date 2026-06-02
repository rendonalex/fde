#!/usr/bin/env python3
"""
Demo script for ADR-1 Intake Agent.

Processes mock AE reports from mock-data/ directory and demonstrates:
1. Format classification
2. Structured data extraction with Claude
3. Confidence scoring and HITL routing
4. RxNorm/MedDRA normalization
5. PV system integration
6. FDA-compliant audit trail generation
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.adr1_intake import ADR1IntakeAgent
from agents.mock_apis import MockRxNormAPI, MockMedDRAAPI, MockPVCaseManagementAPI


def find_mock_data_files(base_path: str) -> List[tuple]:
    """
    Find all mock data files in mock-data/ directory.

    Returns:
        List of (filepath, category) tuples
    """
    mock_data_path = Path(base_path)
    if not mock_data_path.exists():
        raise FileNotFoundError(f"Mock data directory not found: {base_path}")

    files = []

    # Walk through all subdirectories
    for category_dir in mock_data_path.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith('.'):
            for file_path in category_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    # Skip .DS_Store and other hidden files
                    if file_path.suffix in ['.txt', '.json', '.vtt']:
                        files.append((str(file_path), category_dir.name))

    return sorted(files)


def read_file_content(filepath: str) -> str:
    """Read file content with UTF-8 encoding"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def format_extraction_result(result: Dict[str, Any]) -> str:
    """Format extraction result for display"""
    output = []

    output.append("=" * 80)
    output.append("EXTRACTION RESULT")
    output.append("=" * 80)

    # Log
    output.append("\n## Processing Log:")
    for log_entry in result["extraction_log"]:
        output.append(f"  {log_entry}")

    # Routing decision
    output.append(f"\n## Routing Decision: {result['routing_decision']}")

    # Case package summary
    if result["case_package"]:
        pkg = result["case_package"]
        output.append(f"\n## Case Summary:")
        output.append(f"  Case ID: {pkg.case_id}")
        output.append(f"  Status: {pkg.extraction_status}")
        output.append(f"  Format: {pkg.format}")
        output.append(f"  Received: {pkg.received_at}")

        output.append(f"\n  Patient: {pkg.patient.sex}, {pkg.patient.age} years, {pkg.patient.weight} kg (conf: {pkg.patient.confidence:.2f})")
        output.append(f"  Drug: {pkg.suspect_drug.name} {pkg.suspect_drug.dose} (conf: {pkg.suspect_drug.confidence:.2f})")
        if pkg.suspect_drug.rxnorm_code:
            output.append(f"    RxNorm: {pkg.suspect_drug.rxnorm_code}")

        output.append(f"  AE: {pkg.ae_description.narrative[:80]}... (conf: {pkg.ae_description.confidence:.2f})")
        if pkg.ae_description.meddra_pt:
            output.append(f"    MedDRA: {pkg.ae_description.meddra_pt} ({pkg.ae_description.meddra_code})")

        output.append(f"  Temporal: drug start {pkg.temporal.drug_start_date} -> AE onset {pkg.temporal.ae_onset_date} (conf: {pkg.temporal.confidence:.2f})")
        if pkg.temporal.date_estimated:
            output.append(f"    ⚠️  Date estimated from ambiguous text")

        if pkg.concomitant_meds:
            output.append(f"  Concomitant meds: {len(pkg.concomitant_meds)} medications")
            for med in pkg.concomitant_meds[:3]:
                output.append(f"    - {med.name} {med.dose or ''} (conf: {med.confidence:.2f})")

        if pkg.medical_history:
            output.append(f"  Medical history: {pkg.medical_history.narrative[:60]}... (conf: {pkg.medical_history.confidence:.2f})")

        # FDA fields
        output.append(f"\n  [FDA Compliance]")
        output.append(f"  Model version: {pkg.model_version_adr1}")
        output.append(f"  Source documents: {len(pkg.source_documents)} file(s)")
        for doc in pkg.source_documents:
            output.append(f"    - {doc.filename} ({doc.format}) SHA256: {doc.sha256_hash[:16]}...")

        output.append(f"  Span citations: {len(pkg.span_citations)} fields cited")

    else:
        output.append(f"\n## Error: {result.get('error', 'Unknown error')}")

    output.append("\n" + "=" * 80)

    return "\n".join(output)


def run_demo(mock_data_path: str, limit: int = None):
    """
    Run ADR-1 demo on mock data files.

    Args:
        mock_data_path: Path to mock-data directory
        limit: Maximum number of files to process (None = all)
    """
    print("=" * 80)
    print("ADR-1 INTAKE AGENT DEMO")
    print("Helix Therapeutics Pharmacovigilance System")
    print("=" * 80)
    print()

    # Initialize agent with mock APIs
    print("[INIT] Initializing ADR-1 agent with mock APIs...")
    agent = ADR1IntakeAgent(
        rxnorm_api=MockRxNormAPI(simulate_failures=False),
        meddra_api=MockMedDRAAPI(simulate_failures=False),
        pv_api=MockPVCaseManagementAPI(simulate_failures=False),
        simulate_failures=False
    )
    print("[INIT] Agent ready\n")

    # Find mock data files
    print(f"[SCAN] Scanning {mock_data_path} for test files...")
    files = find_mock_data_files(mock_data_path)
    print(f"[SCAN] Found {len(files)} files\n")

    if limit:
        files = files[:limit]
        print(f"[LIMIT] Processing first {limit} files\n")

    # Process each file
    results = []
    for idx, (filepath, category) in enumerate(files, 1):
        filename = os.path.basename(filepath)
        print(f"\n[{idx}/{len(files)}] Processing: {filename} (category: {category})")
        print("-" * 80)

        # Read file
        content = read_file_content(filepath)
        print(f"[READ] File size: {len(content)} bytes")

        # Process with ADR-1
        result = agent.process_report(filename, content)
        results.append({
            "filename": filename,
            "category": category,
            "result": result
        })

        # Display result
        print(format_extraction_result(result))

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    total = len(results)
    auto_complete = sum(1 for r in results if r["result"]["routing_decision"] == "ADR-2")
    hitl_required = sum(1 for r in results if r["result"]["routing_decision"] == "HITL_QUEUE")
    exceptions = sum(1 for r in results if r["result"]["routing_decision"] == "EXCEPTION_QUEUE")
    duplicates = sum(1 for r in results if r["result"]["routing_decision"] == "PENDING_DUPLICATE")
    errors = sum(1 for r in results if r["result"]["case_package"] is None)

    print(f"\nTotal cases processed: {total}")
    print(f"  ✓ AUTO_COMPLETE → ADR-2: {auto_complete} ({auto_complete/total*100:.1f}%)")
    print(f"  ⚠️  HUMAN_REQUIRED → HITL: {hitl_required} ({hitl_required/total*100:.1f}%)")
    print(f"  ⛔ EXCEPTION_NOTE: {exceptions} ({exceptions/total*100:.1f}%)")
    print(f"  🔄 PENDING_DUPLICATE: {duplicates} ({duplicates/total*100:.1f}%)")
    print(f"  ❌ Errors: {errors} ({errors/total*100:.1f}%)")

    # Confidence distribution
    confidences = []
    for r in results:
        if r["result"]["case_package"]:
            pkg = r["result"]["case_package"]
            confidences.extend([
                pkg.patient.confidence,
                pkg.suspect_drug.confidence,
                pkg.ae_description.confidence,
                pkg.temporal.confidence
            ])

    if confidences:
        avg_confidence = sum(confidences) / len(confidences)
        print(f"\nAverage extraction confidence: {avg_confidence:.3f}")
        print(f"Min: {min(confidences):.3f}, Max: {max(confidences):.3f}")

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ADR-1 Intake Agent Demo")
    parser.add_argument(
        "--mock-data",
        default="../mock-data",
        help="Path to mock-data directory (default: ../mock-data)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of files to process (default: all)"
    )
    parser.add_argument(
        "--output",
        help="Save results to JSON file"
    )

    args = parser.parse_args()

    # Resolve mock-data path
    script_dir = Path(__file__).parent
    mock_data_path = (script_dir / args.mock_data).resolve()

    # Run demo
    results = run_demo(str(mock_data_path), limit=args.limit)

    # Save results if requested
    if args.output:
        output_data = []
        for r in results:
            output_data.append({
                "filename": r["filename"],
                "category": r["category"],
                "case_id": r["result"]["case_package"].case_id if r["result"]["case_package"] else None,
                "extraction_status": str(r["result"]["case_package"].extraction_status) if r["result"]["case_package"] else None,
                "routing_decision": r["result"]["routing_decision"],
                "error": r["result"].get("error")
            })

        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n[SAVE] Results saved to {args.output}")
