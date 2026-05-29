"""
Pattern Library: Storage and retrieval of insurer-specific patterns
"""
from typing import Optional, List, Dict
from datetime import date
from .models import InsurerPattern, DenialPattern, ConfidenceLevel, InsurerName


class PatternLibrary:
    """
    Manages insurer-specific SLA patterns and denial patterns.
    In production, this would be backed by a database.
    For prototype, uses in-memory storage with JSON serialization.
    """

    def __init__(self):
        self.insurer_patterns: Dict[str, InsurerPattern] = {}
        self.denial_patterns: List[DenialPattern] = []
        self._seed_initial_patterns()

    def _seed_initial_patterns(self):
        """Seed with patterns extracted from Dana's Google Sheet (Artefact 5.1)"""

        # Humana: Always exactly 6 days, never 5
        self.insurer_patterns["Humana"] = InsurerPattern(
            insurer_name="Humana",
            sla_days=6,
            confidence=ConfidenceLevel.HIGH,
            sample_size=50,
            last_updated=date(2026, 3, 15),
            variance_days=0.2,  # Very consistent
            notes="Always exactly 6 days; never 5 (stated SLA). Pattern stable for 2+ years.",
            is_predictable=True
        )

        # UnitedHealthcare Choice: 6-7 days
        self.insurer_patterns["UnitedHealthcare Choice"] = InsurerPattern(
            insurer_name="UnitedHealthcare Choice",
            sla_days=7,
            confidence=ConfidenceLevel.HIGH,
            sample_size=40,
            last_updated=date(2026, 1, 20),
            variance_days=0.8,  # Slight variance (6-7 days)
            notes="Usually 7 days, occasionally 6. Pattern changed 18 months ago from 5 days.",
            is_predictable=True
        )

        # BCBS PPO: 3 days
        self.insurer_patterns["BCBS PPO"] = InsurerPattern(
            insurer_name="BCBS PPO",
            sla_days=3,
            confidence=ConfidenceLevel.HIGH,
            sample_size=30,
            last_updated=date(2026, 2, 10),
            variance_days=0.5,
            notes="Fast processor; typically 3 days.",
            is_predictable=True
        )

        # Medicare: 4-5 days
        self.insurer_patterns["Medicare"] = InsurerPattern(
            insurer_name="Medicare",
            sla_days=5,
            confidence=ConfidenceLevel.MEDIUM,
            sample_size=35,
            last_updated=date(2026, 3, 1),
            variance_days=1.0,
            notes="Usually 4-5 days. Medicare Advantage may differ.",
            is_predictable=True
        )

        # Wellpath: 7 days (Medicaid managed care)
        self.insurer_patterns["Wellpath"] = InsurerPattern(
            insurer_name="Wellpath",
            sla_days=7,
            confidence=ConfidenceLevel.HIGH,
            sample_size=25,
            last_updated=date(2026, 3, 20),
            variance_days=1.2,
            notes="Medicaid managed care. Usually 7 days. Known denial patterns for colonoscopy.",
            is_predictable=True
        )

        # Aetna: Unpredictable (3-7 days)
        self.insurer_patterns["Aetna"] = InsurerPattern(
            insurer_name="Aetna",
            sla_days=5,  # Median, but not reliable
            confidence=ConfidenceLevel.LOW,
            sample_size=20,
            last_updated=date(2026, 3, 25),
            variance_days=2.5,  # High variance
            notes="UNPREDICTABLE: Sometimes 3 days, sometimes 7+. No stable pattern. Always escalate to Dana.",
            is_predictable=False  # Critical flag
        )

        # Wellpath colonoscopy denial pattern (from Artefact 5.1 footer)
        self.denial_patterns.append(DenialPattern(
            insurer_name="Wellpath",
            procedure_type="Colonoscopy",
            denial_reason_pattern="medical necessity|prior authorization denied",
            workaround_suggestion="Attach prior visit note (standing rule: include with submission to avoid resubmit cycle)",
            occurrence_count=35,  # 30-40 occurrences over 6 years per coach validation
            confidence=ConfidenceLevel.HIGH,
            last_seen=date(2026, 3, 15)
        ))

    def get_pattern(self, insurer_name: str) -> Optional[InsurerPattern]:
        """Retrieve insurer pattern (exact match)"""
        return self.insurer_patterns.get(insurer_name)

    def update_pattern(self, insurer_name: str, new_sla_days: int, reason: str) -> InsurerPattern:
        """Update insurer SLA pattern (requires Dana approval in production)"""
        if insurer_name in self.insurer_patterns:
            pattern = self.insurer_patterns[insurer_name]
            pattern.sla_days = new_sla_days
            pattern.last_updated = date.today()
            pattern.notes = f"{pattern.notes} | UPDATED: {reason} on {date.today()}"
            return pattern
        else:
            # Create new pattern for unknown insurer
            new_pattern = InsurerPattern(
                insurer_name=insurer_name,
                sla_days=new_sla_days,
                confidence=ConfidenceLevel.LOW,  # New pattern = low confidence
                sample_size=1,
                last_updated=date.today(),
                variance_days=0.0,
                notes=f"New pattern created: {reason}",
                is_predictable=True  # Assume predictable until proven otherwise
            )
            self.insurer_patterns[insurer_name] = new_pattern
            return new_pattern

    def find_denial_pattern(self, insurer_name: str, procedure_type: str, denial_reason: str) -> Optional[DenialPattern]:
        """
        Match denial reason to known patterns (semantic search in production).
        For prototype, uses simple keyword matching.
        """
        for pattern in self.denial_patterns:
            if pattern.insurer_name == insurer_name and pattern.procedure_type.lower() in procedure_type.lower():
                # Simple keyword match (in production, use semantic similarity)
                if any(keyword in denial_reason.lower() for keyword in pattern.denial_reason_pattern.split("|")):
                    return pattern
        return None

    def list_all_patterns(self) -> List[InsurerPattern]:
        """Return all insurer patterns"""
        return list(self.insurer_patterns.values())

    def get_predictable_insurers(self) -> List[str]:
        """Return list of insurers with stable patterns (for autonomous operation)"""
        return [
            name for name, pattern in self.insurer_patterns.items()
            if pattern.is_predictable and pattern.confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]
        ]

    def get_unpredictable_insurers(self) -> List[str]:
        """Return list of insurers requiring escalation (Aetna-like)"""
        return [
            name for name, pattern in self.insurer_patterns.items()
            if not pattern.is_predictable or pattern.confidence == ConfidenceLevel.LOW
        ]
