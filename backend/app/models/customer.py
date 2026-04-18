from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tags: list[str] = []
    notes: Optional[str] = None
    lead_id: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None


class CustomerOut(BaseModel):
    id: str
    org_id: str
    lead_id: Optional[str]
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    tags: list[str]
    lifetime_value: float
    total_orders: int
    last_purchase_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
