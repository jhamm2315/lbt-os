from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator


EXPENSE_CATEGORIES = {
    "payroll", "materials", "marketing", "rent", "utilities",
    "equipment", "insurance", "software", "misc",
}


class ExpenseCreate(BaseModel):
    category: str
    description: str
    amount: float
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    is_recurring: bool = False
    recurrence_period: Optional[str] = None
    expense_date: date = date.today()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in EXPENSE_CATEGORIES:
            raise ValueError(f"category must be one of {EXPENSE_CATEGORIES}")
        return v

    @field_validator("amount")
    @classmethod
    def positive_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v


class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_period: Optional[str] = None
    expense_date: Optional[date] = None


class ExpenseOut(BaseModel):
    id: str
    org_id: str
    category: str
    description: str
    amount: float
    vendor: Optional[str]
    receipt_url: Optional[str]
    is_recurring: bool
    recurrence_period: Optional[str]
    expense_date: date
    created_at: datetime
    updated_at: datetime
