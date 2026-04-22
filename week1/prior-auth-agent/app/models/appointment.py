"""Appointment entity [per Claude.md Section 2]."""
import enum
from datetime import datetime, time
from sqlalchemy import Column, String, DateTime, Time, Enum, Boolean, Text
from app.database import Base


class AppointmentStatus(str, enum.Enum):
    """Appointment status."""

    SCHEDULED = "SCHEDULED"
    CHECKED_IN = "CHECKED_IN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Appointment(Base):
    """
    Scheduled patient visit (sourced from athenahealth EHR).

    Subset of fields relevant to prior-auth checking.
    """

    __tablename__ = "appointments"

    # Primary identification
    appointment_id = Column(String(255), primary_key=True)
    patient_id = Column(String(255), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    scheduled_time = Column(Time, nullable=False)
    appointment_type = Column(String(100), nullable=True)

    # Procedure details (stored as comma-separated codes/descriptions)
    procedure_codes = Column(Text, nullable=True)  # Comma-separated CPT codes
    procedure_descriptions = Column(Text, nullable=True)  # Comma-separated descriptions

    # Insurance
    insurance_policy_id = Column(String(255), nullable=False, index=True)

    # Status
    appointment_status = Column(
        Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED, index=True
    )

    # Prior-auth tracking
    prior_auth_check_id = Column(String(255), nullable=True, index=True)
    prior_auth_verified = Column(Boolean, nullable=False, default=False)
    prior_auth_verified_at = Column(DateTime, nullable=True)

    # Audit
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_procedure_codes_list(self):
        """Get list of procedure CPT codes."""
        if not self.procedure_codes:
            return []
        return [code.strip() for code in self.procedure_codes.split(",") if code.strip()]

    def set_procedure_codes_list(self, codes):
        """Set list of procedure CPT codes."""
        self.procedure_codes = ",".join(codes) if codes else None

    def get_procedure_descriptions_list(self):
        """Get list of procedure descriptions."""
        if not self.procedure_descriptions:
            return []
        return [desc.strip() for desc in self.procedure_descriptions.split(",") if desc.strip()]

    def set_procedure_descriptions_list(self, descriptions):
        """Set list of procedure descriptions."""
        self.procedure_descriptions = ",".join(descriptions) if descriptions else None

    def __repr__(self):
        return (
            f"<Appointment(appointment_id='{self.appointment_id}', "
            f"patient_id='{self.patient_id}', "
            f"scheduled_date={self.scheduled_date})>"
        )
