from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


PAYMENT_STATUSES = {"pending", "paid", "refunded"}


class SaleCreate(BaseModel):
    customer_id: Optional[str] = None
    lead_id: Optional[str] = None
    service: str
    amount: float
    cost: float = 0.0
    payment_method: Optional[str] = None
    payment_status: str = "pending"
    source: Optional[str] = None
    invoice_number: Optional[str] = None
    notes: Optional[str] = None
    sold_at: Optional[datetime] = None

    @field_validator("amount", "cost")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("amount and cost must be >= 0")
        return v

    @field_validator("payment_status")
    @classmethod
    def validate_payment_status(cls, v: str) -> str:
        if v not in PAYMENT_STATUSES:
            raise ValueError(f"payment_status must be one of {PAYMENT_STATUSES}")
        return v


class SaleUpdate(BaseModel):
    service: Optional[str] = None
    amount: Optional[float] = None
    cost: Optional[float] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    source: Optional[str] = None
    invoice_number: Optional[str] = None
    notes: Optional[str] = None
    sold_at: Optional[datetime] = None


class SaleOut(BaseModel):
    id: str
    org_id: str
    customer_id: Optional[str]
    lead_id: Optional[str]
    service: str
    amount: float
    cost: float
    profit: float
    payment_method: Optional[str]
    payment_status: str
    source: Optional[str]
    invoice_number: Optional[str]
    notes: Optional[str]
    sold_at: datetime
    created_at: datetime
    updated_at: datetime
