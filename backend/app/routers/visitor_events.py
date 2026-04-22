from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from ..database import get_db
from ..models.visitor_event import VisitorEventCreate
from ..routers.admin import get_admin_auth
from ..services import visitor_events

router = APIRouter(prefix="/visitor-events", tags=["visitor-events"])


@router.post("", status_code=202)
def capture_visitor_event(body: VisitorEventCreate, request: Request):
    """Public event intake for arrivals, CTA clicks, and onboarding submissions."""
    return visitor_events.record_event(get_db(), body, request)


@router.get("/recent")
def recent_visitor_events(
    admin: Annotated[dict, Depends(get_admin_auth)],
    limit: int = Query(50, ge=1, le=200),
):
    return {"events": visitor_events.list_recent_events(get_db(), limit)}


@router.get("/summary")
def visitor_event_summary(
    admin: Annotated[dict, Depends(get_admin_auth)],
    days: int = Query(7, ge=1, le=90),
):
    return visitor_events.event_summary(get_db(), days)

