from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


SUPPORTED_PROVIDERS = {"quickbooks", "hubspot", "stripe"}
SYNC_STATUSES = {"connected", "disconnected", "error"}
RUN_STATUSES = {"pending", "running", "success", "partial", "failed"}


class IntegrationConnectionCreate(BaseModel):
    provider: str
    label: Optional[str] = None
    credentials: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)
    external_account_id: Optional[str] = None
    external_account_name: Optional[str] = None

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        if value not in SUPPORTED_PROVIDERS:
            raise ValueError(f"provider must be one of {sorted(SUPPORTED_PROVIDERS)}")
        return value


class IntegrationConnectionUpdate(BaseModel):
    label: Optional[str] = None
    credentials: Optional[dict[str, Any]] = None
    config: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    external_account_id: Optional[str] = None
    external_account_name: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in SYNC_STATUSES:
            raise ValueError(f"status must be one of {SYNC_STATUSES}")
        return value


class IntegrationConnectionOut(BaseModel):
    id: str
    org_id: str
    provider: str
    label: Optional[str]
    status: str
    config: dict[str, Any]
    external_account_id: Optional[str]
    external_account_name: Optional[str]
    last_synced_at: Optional[datetime]
    last_sync_status: Optional[str]
    last_sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime


class IntegrationSyncRunOut(BaseModel):
    id: str
    org_id: str
    connection_id: str
    provider: str
    trigger_source: str
    status: str
    stats: dict[str, Any]
    error: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
