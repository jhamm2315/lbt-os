from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ..auth import AuthContext, get_auth
from ..database import get_db
from ..services.metrics import get_dashboard_metrics, get_revenue_trend

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/dashboard")
def dashboard_metrics(
    auth: Annotated[AuthContext, Depends(get_auth)],
    days: int = Query(30, ge=7, le=365),
):
    """
    All dashboard KPIs for the org.
    Single endpoint — frontend fetches once, renders everything.
    """
    db = get_db()
    return get_dashboard_metrics(db, auth.org_id, days=days)


@router.get("/revenue-trend")
def revenue_trend(
    auth: Annotated[AuthContext, Depends(get_auth)],
    weeks: int = Query(12, ge=4, le=52),
):
    """Daily revenue data points for the last N weeks (for chart rendering)."""
    db = get_db()
    return get_revenue_trend(db, auth.org_id, weeks=weeks)
