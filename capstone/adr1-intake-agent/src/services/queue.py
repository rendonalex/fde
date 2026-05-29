"""Queue management for SLA-aware claim routing."""

from datetime import datetime, timedelta

from ..models import NormalizedClaimRecord, SLAQueue


class QueueManager:
    """Manages SLA-aware claim queue assignment."""

    def assign_queue(self, claim: NormalizedClaimRecord) -> tuple[SLAQueue, datetime]:
        """
        Assign claim to SLA queue and compute deadline.

        Simplified logic:
        - PRIORITY: prior_auth_required or payer_name contains "Medicaid"
        - STANDARD: everything else
        - Deadline: 7 days from now

        Real implementation would use payer SLA config.
        """
        # Determine queue tier
        if claim.prior_auth_required:
            queue = SLAQueue.PRIORITY
        elif "medicaid" in claim.payer_name.lower():
            queue = SLAQueue.PRIORITY
        else:
            queue = SLAQueue.STANDARD

        # Compute deadline
        deadline = datetime.utcnow() + timedelta(days=7)

        return queue, deadline
