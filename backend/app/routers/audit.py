from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ..auth import AuthContext, get_auth, require_plan
from ..database import get_db
from ..services.ai_audit import get_latest_audit, run_audit

router = APIRouter(prefix="/audit", tags=["ai-audit"])


@router.post("/run", dependencies=[Depends(require_plan("pro"))])
def trigger_audit(auth: Annotated[AuthContext, Depends(get_auth)]):
    """
    Trigger a fresh AI audit for this organization.
    Requires pro plan or higher.
    Each run costs ~$0.002 with gpt-4o-mini — rate limiting is prudent.
    """
    db = get_db()
    org = db.table("organizations").select("name, industry").eq("id", auth.org_id).single().execute()
    if not org.data:
        raise HTTPException(status_code=404, detail="Organization not found.")

    report = run_audit(
        db=db,
        org_id=auth.org_id,
        org_name=org.data["name"],
        industry=org.data.get("industry"),
    )
    return report


@router.get("/latest", dependencies=[Depends(require_plan("pro"))])
def get_latest(auth: Annotated[AuthContext, Depends(get_auth)]):
    """Return the most recent audit report without triggering a new one."""
    db = get_db()
    report = get_latest_audit(db, auth.org_id)
    if not report:
        raise HTTPException(
            status_code=404,
            detail="No audit report found. Run your first audit to get insights.",
        )
    return report


@router.get("/history", dependencies=[Depends(require_plan("pro"))])
def audit_history(
    auth: Annotated[AuthContext, Depends(get_auth)],
    limit: int = 10,
):
    """Return past audit reports (summary only) for trend tracking."""
    db = get_db()
    result = (
        db.table("audit_reports")
        .select("id, period_start, period_end, health_score, generated_at")
        .eq("org_id", auth.org_id)
        .order("generated_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
