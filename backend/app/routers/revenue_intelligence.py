"""
Revenue Intelligence endpoints — pipeline analytics and CRM health.
All endpoints require a valid auth token (any plan).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from ..auth import AuthContext, get_auth
from ..database import get_db
from ..limiter import limiter
from ..services import revenue_intelligence as ri

router = APIRouter(prefix="/revenue-intelligence", tags=["revenue-intelligence"])


@router.get("/ltv")
@limiter.limit("60/hour")
def ltv_metrics(request: Request, auth: Annotated[AuthContext, Depends(get_auth)]):
    return ri.get_ltv_metrics(get_db(), auth.org_id)


@router.get("/stage-velocity")
@limiter.limit("60/hour")
def stage_velocity(
    request: Request,
    auth: Annotated[AuthContext, Depends(get_auth)],
    days: int = Query(90, ge=7, le=365),
):
    return ri.get_stage_velocity(get_db(), auth.org_id, days)


@router.get("/win-loss")
@limiter.limit("60/hour")
def win_loss_cohort(
    request: Request,
    auth: Annotated[AuthContext, Depends(get_auth)],
    days: int = Query(90, ge=7, le=365),
):
    return ri.get_win_loss_cohort(get_db(), auth.org_id, days)


@router.get("/data-quality")
@limiter.limit("30/hour")
def data_quality(request: Request, auth: Annotated[AuthContext, Depends(get_auth)]):
    return ri.get_data_quality_scorecard(get_db(), auth.org_id)


@router.get("/expansion")
@limiter.limit("60/hour")
def expansion_signals(request: Request, auth: Annotated[AuthContext, Depends(get_auth)]):
    return ri.get_expansion_signals(get_db(), auth.org_id)


@router.get("/speed-to-lead")
@limiter.limit("60/hour")
def speed_to_lead(
    request: Request,
    auth: Annotated[AuthContext, Depends(get_auth)],
    days: int = Query(30, ge=7, le=365),
):
    return ri.get_speed_to_lead(get_db(), auth.org_id, days)


@router.get("/stage-aging")
@limiter.limit("60/hour")
def stage_aging(request: Request, auth: Annotated[AuthContext, Depends(get_auth)]):
    return ri.get_stage_aging(get_db(), auth.org_id)
