from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class OrgCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    city: str = "Denver"
    state: str = "CO"


class OrgUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    onboarding_complete: Optional[bool] = None


class OrgOut(BaseModel):
    id: str
    clerk_org_id: str
    name: str
    industry: Optional[str]
    plan: str
    subscription_status: str
    city: str
    state: str
    onboarding_complete: bool
    created_at: datetime
