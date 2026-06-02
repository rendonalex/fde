"""
ADR-1 → ADR-2 Workflow Orchestrator

Coordinates end-to-end adverse event processing pipeline:
1. ADR-1 Intake: Extract structured data from raw reports
2. Routing: AUTO_COMPLETE → ADR-2, HUMAN_REQUIRED → HITL queue
3. ADR-2 Triage: Classify seriousness, expectedness, reportability
4. MSO Queue: Route cases requiring deep review

Provides batch processing, error handling, and summary statistics.
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.adr1_intake import ADR1IntakeAgent
from agents.adr2_triage import ADR2TriageAgent
from agents.models import AECasePackage, TriageRecommendation


class WorkflowOrchestrator:
    """
    Orchestrates ADR-1 → ADR-2 pipeline for batch adverse event processing.
    """

    def __init__(self, anthropic_api_key: str):
        """
        Initialize orchestrator with API credentials.

        Args:
            anthropic_api_key: Anthropic API key for Claude integration
        """
        self.api_key = anthropic_api_key
        self.adr1_agent = ADR1IntakeAgent(api_key=anthropic_api_key)
        self.adr2_agent = ADR2TriageAgent(anthropic_api_key=anthropic_api_key)

        # Statistics
        self.stats = {
            "total_cases": 0,
            "adr1_success": 0,
            "adr1_failed": 0,
            "routed_to_adr2": 0,
            "routed_to_hitl": 0,
            "routed_to_exception": 0,
            "routed_to_duplicate": 0,
            "adr2_success": 0,
            "adr2_failed": 0,
            "reportability": {
                "15_DAY_EXPEDITED": 0,
                "PERIODIC": 0,
                "NON_REPORTABLE": 0
            },
            "mso_deep_review_required": 0,
            "signal_detections": 0
        }

        # Results storage
        self.results: List[Dict[str, Any]] = []

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single AE report file through ADR-1 → ADR-2 pipeline.

        Args:
            file_path: Path to AE report file

        Returns:
            Dict with processing results and routing decisions
        """
        result = {
            "file": file_path,
            "timestamp": datetime.now().isoformat(),
            "adr1_status": None,
            "routing": None,
            "adr2_status": None,
            "case_package": None,
            "triage_recommendation": None,
            "error": None
        }

        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Step 1: ADR-1 Intake
            adr1_result = self.adr1_agent.process_report(
                filename=file_path,
                content=content
            )

            if not adr1_result["case_package"]:
                # ADR-1 extraction failed
                result["adr1_status"] = "FAILED"
                result["error"] = adr1_result.get("error")
                result["routing"] = adr1_result["routing_decision"]
                self.stats["adr1_failed"] += 1
                return result

            # ADR-1 success
            result["adr1_status"] = "SUCCESS"
            result["case_package"] = adr1_result["case_package"].dict()
            result["routing"] = adr1_result["routing_decision"]
            self.stats["adr1_success"] += 1

            # Route based on ADR-1 decision
            if "ADR-2" in result["routing"]:
                # Route to ADR-2 Triage
                self.stats["routed_to_adr2"] += 1

                try:
                    # Step 2: ADR-2 Triage
                    triage_recommendation, classification_log = self.adr2_agent.classify_case(
                        adr1_result["case_package"]
                    )

                    result["adr2_status"] = "SUCCESS"
                    result["triage_recommendation"] = triage_recommendation.dict()
                    self.stats["adr2_success"] += 1

                    # Update reportability stats
                    reportability_type = triage_recommendation.reportability_recommendation.recommendation.value
                    self.stats["reportability"][reportability_type] += 1

                    # Update MSO deep review stats
                    if triage_recommendation.mso_flags.deep_review_required:
                        self.stats["mso_deep_review_required"] += 1

                    # Update signal detection stats
                    if triage_recommendation.signal_detection_flag:
                        self.stats["signal_detections"] += 1

                except Exception as e:
                    result["adr2_status"] = "FAILED"
                    result["error"] = f"ADR-2 classification failed: {str(e)}"
                    self.stats["adr2_failed"] += 1

            elif "HITL" in result["routing"]:
                self.stats["routed_to_hitl"] += 1

            elif "EXCEPTION" in result["routing"]:
                self.stats["routed_to_exception"] += 1

            elif "DUPLICATE" in result["routing"]:
                self.stats["routed_to_duplicate"] += 1

        except Exception as e:
            result["adr1_status"] = "FAILED"
            result["error"] = f"File processing error: {str(e)}"
            self.stats["adr1_failed"] += 1

        return result

    def process_directory(
        self,
        input_dir: str,
        output_file: str = None,
        file_pattern: str = "*.txt"
    ) -> Dict[str, Any]:
        """
        Process all AE reports in a directory through the pipeline.

        Args:
            input_dir: Directory containing AE report files
            output_file: Optional path to save results JSON
            file_pattern: Glob pattern for files to process (default: *.txt)

        Returns:
            Dict with summary statistics and results
        """
        print(f"\n{'='*80}")
        print(f"ADR-1 → ADR-2 WORKFLOW ORCHESTRATOR")
        print(f"{'='*80}\n")

        print(f"Input Directory: {input_dir}")
        print(f"File Pattern: {file_pattern}")

        # Find files
        input_path = Path(input_dir)
        files = list(input_path.rglob(file_pattern))

        print(f"Found {len(files)} files to process\n")

        if len(files) == 0:
            print("⚠️  No files found matching pattern")
            return {"stats": self.stats, "results": []}

        # Process each file
        for i, file_path in enumerate(files, 1):
            print(f"[{i}/{len(files)}] Processing: {file_path.name}")

            result = self.process_file(str(file_path))
            self.results.append(result)
            self.stats["total_cases"] += 1

            # Show routing decision
            routing = result["routing"]
            if result["adr1_status"] == "FAILED":
                print(f"  ❌ ADR-1 failed: {result['error'][:60]}...")
            elif "ADR-2" in routing:
                if result["adr2_status"] == "SUCCESS":
                    rec = result["triage_recommendation"]
                    reportability = rec["reportability_recommendation"]["recommendation"]
                    print(f"  ✅ ADR-1 → ADR-2 → {reportability}")
                else:
                    print(f"  ⚠️  ADR-1 → ADR-2 failed: {result['error'][:60]}...")
            else:
                print(f"  ⚠️  ADR-1 → {routing}")

        # Generate summary
        print(f"\n{'='*80}")
        print(f"WORKFLOW SUMMARY")
        print(f"{'='*80}\n")

        print(f"**Total Cases Processed:** {self.stats['total_cases']}")
        print(f"\n**ADR-1 Intake:**")
        print(f"  Success: {self.stats['adr1_success']}")
        print(f"  Failed: {self.stats['adr1_failed']}")

        print(f"\n**Routing Decisions:**")
        print(f"  → ADR-2 Triage: {self.stats['routed_to_adr2']}")
        print(f"  → HITL Queue: {self.stats['routed_to_hitl']}")
        print(f"  → Exception Queue: {self.stats['routed_to_exception']}")
        print(f"  → Duplicate Review: {self.stats['routed_to_duplicate']}")

        if self.stats['routed_to_adr2'] > 0:
            print(f"\n**ADR-2 Triage:**")
            print(f"  Success: {self.stats['adr2_success']}")
            print(f"  Failed: {self.stats['adr2_failed']}")

            print(f"\n**Reportability Breakdown:**")
            for rep_type, count in self.stats['reportability'].items():
                print(f"  {rep_type}: {count}")

            print(f"\n**MSO Deep Review Required:** {self.stats['mso_deep_review_required']}")
            print(f"**Signal Detections (3-cases-in-90-days):** {self.stats['signal_detections']}")

        # Calculate success rate
        if self.stats['total_cases'] > 0:
            success_rate = (self.stats['adr1_success'] / self.stats['total_cases']) * 100
            print(f"\n**Overall Success Rate:** {success_rate:.1f}%")

        # Save results if output file specified
        if output_file:
            output_data = {
                "summary": self.stats,
                "results": self.results,
                "generated_at": datetime.now().isoformat()
            }

            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            print(f"\n📁 Results saved to: {output_file}")

        print(f"\n{'='*80}\n")

        return {
            "stats": self.stats,
            "results": self.results
        }

    def get_expedited_cases(self) -> List[Dict[str, Any]]:
        """
        Get all cases requiring 15-day expedited reporting.

        Returns:
            List of case results with EXPEDITED_15_DAY reportability
        """
        expedited = []
        for result in self.results:
            if result.get("triage_recommendation"):
                rec = result["triage_recommendation"]
                if rec["reportability_recommendation"]["recommendation"] == "15_DAY_EXPEDITED":
                    expedited.append(result)
        return expedited

    def get_mso_queue(self) -> List[Dict[str, Any]]:
        """
        Get all cases requiring MSO deep review.

        Returns:
            List of case results flagged for MSO review
        """
        mso_queue = []
        for result in self.results:
            if result.get("triage_recommendation"):
                rec = result["triage_recommendation"]
                if rec["mso_flags"]["deep_review_required"]:
                    mso_queue.append(result)
        return mso_queue

    def get_hitl_queue(self) -> List[Dict[str, Any]]:
        """
        Get all cases requiring HITL case processor re-key.

        Returns:
            List of case results routed to HITL
        """
        hitl_queue = []
        for result in self.results:
            if "HITL" in result.get("routing", ""):
                hitl_queue.append(result)
        return hitl_queue


def main():
    """Demo: Process test-adr2 directory through full pipeline"""
    import sys

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator(anthropic_api_key=api_key)

    # Process test directory
    input_dir = "mock-data/test-adr2"
    output_file = "workflow_results.json"

    results = orchestrator.process_directory(
        input_dir=input_dir,
        output_file=output_file,
        file_pattern="*.txt"
    )

    # Show expedited cases
    expedited_cases = orchestrator.get_expedited_cases()
    if expedited_cases:
        print(f"\n⚠️  {len(expedited_cases)} case(s) require 15-DAY EXPEDITED reporting:")
        for case in expedited_cases:
            case_id = case["case_package"]["case_id"]
            file_name = Path(case["file"]).name
            print(f"  - {file_name} (Case ID: {case_id})")

    # Show MSO queue
    mso_queue = orchestrator.get_mso_queue()
    if mso_queue:
        print(f"\n👨‍⚕️ {len(mso_queue)} case(s) in MSO Deep Review Queue:")
        for case in mso_queue:
            case_id = case["case_package"]["case_id"]
            file_name = Path(case["file"]).name
            reasons = case["triage_recommendation"]["mso_flags"]["reason"]
            print(f"  - {file_name}: {', '.join(reasons)}")


if __name__ == "__main__":
    main()
