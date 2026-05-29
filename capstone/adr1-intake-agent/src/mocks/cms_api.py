"""Mock CMS API using in-memory SQLite store."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ..models import NormalizedClaimRecord


class MockCMSAPI:
    """Mock Claims Management System API."""

    def __init__(self):
        self.claims: dict[UUID, NormalizedClaimRecord] = {}

    async def create_claim(self, claim: NormalizedClaimRecord) -> dict:
        """Create claim record (POST /v1/claims)."""
        # Check for duplicate
        duplicate = await self.check_duplicate(
            claim.source_claim_ref, claim.member_id, claim.date_of_service_start
        )
        if duplicate:
            return {
                "error": "DUPLICATE_CLAIM",
                "existing_claim_id": str(duplicate),
                "status": 409,
            }

        # Generate claim_id and timestamps
        claim.claim_id = uuid4()
        claim.created_at = datetime.utcnow()
        claim.updated_at = datetime.utcnow()
        claim.queue_assigned_at = datetime.utcnow()

        # Store claim
        self.claims[claim.claim_id] = claim

        return {"claim_id": str(claim.claim_id), "created_at": claim.created_at, "status": 201}

    async def get_claim(self, claim_id: UUID) -> Optional[NormalizedClaimRecord]:
        """Get claim by ID (GET /v1/claims/{claim_id})."""
        return self.claims.get(claim_id)

    async def check_duplicate(
        self, source_ref: str, member_id: str, dos_start: str
    ) -> Optional[UUID]:
        """Check for duplicate claim."""
        for cid, claim in self.claims.items():
            if (
                claim.source_claim_ref == source_ref
                and claim.member_id == member_id
                and claim.date_of_service_start == dos_start
            ):
                return cid
        return None
