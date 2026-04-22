"""PriorAuthRecord entity [per Claude.md Section 2]."""
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Integer, Text
from app.database import Base


class ApprovalStatus(str, enum.Enum):
    """Prior-authorization approval status."""

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    PENDING = "PENDING"


class PriorAuthRecord(Base):
    """
    Prior-authorization approval record.

    Represents a prior-auth approval from an insurance company,
    stored in the prior-auth database.
    """

    __tablename__ = "prior_auth_records"

    # Primary identification
    prior_auth_id = Column(String(255), primary_key=True)
    patient_id = Column(String(255), nullable=False, index=True)
    insurance_policy_id = Column(String(255), nullable=False, index=True)

    # Approval details
    approval_number = Column(String(255), nullable=False, unique=True, index=True)
    approval_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=False, index=True)
    approval_status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.ACTIVE, index=True)

    # Covered services (stored as comma-separated CPT codes for simplicity)
    approved_cpt_codes = Column(Text, nullable=True)  # Comma-separated CPT codes
    approved_service_description = Column(Text, nullable=True)
    service_category = Column(String(100), nullable=True)

    # Limitations
    approved_units = Column(Integer, nullable=True)  # null = unlimited
    units_used = Column(Integer, nullable=False, default=0)

    # Source metadata
    source_system = Column(String(100), nullable=False, default="prior_auth_db")
    last_verified_at = Column(DateTime, nullable=True)

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_approved_cpt_codes_list(self):
        """Get list of approved CPT codes."""
        if not self.approved_cpt_codes:
            return []
        return [code.strip() for code in self.approved_cpt_codes.split(",") if code.strip()]

    def set_approved_cpt_codes_list(self, codes):
        """Set list of approved CPT codes."""
        self.approved_cpt_codes = ",".join(codes) if codes else None

    def __repr__(self):
        return (
            f"<PriorAuthRecord(prior_auth_id='{self.prior_auth_id}', "
            f"approval_number='{self.approval_number}', "
            f"status={self.approval_status})>"
        )
