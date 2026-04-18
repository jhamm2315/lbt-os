from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


LEAD_STATUSES = {"new", "contacted", "qualified", "proposal", "won", "lost"}
LEAD_SOURCES  = {"google", "referral", "social", "yelp", "cold_call", "walk_in", "website", "other"}


class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: str = "new"
    service_interest: Optional[str] = None
    estimated_value: Optional[float] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    follow_up_at: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in LEAD_STATUSES:
            raise ValueError(f"status must be one of {LEAD_STATUSES}")
        return v


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    service_interest: Optional[str] = None
    estimated_value: Optional[float] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    contacted_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    lost_reason: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in LEAD_STATUSES:
            raise ValueError(f"status must be one of {LEAD_STATUSES}")
        return v


class LeadOut(BaseModel):
    id: str
    org_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    source: Optional[str]
    status: str
    service_interest: Optional[str]
    estimated_value: Optional[float]
    notes: Optional[str]
    assigned_to: Optional[str]
    follow_up_at: Optional[datetime]
    contacted_at: Optional[datetime]
    converted_at: Optional[datetime]
    lost_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
