from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ..auth import AuthContext, UserContext, get_auth, get_user
from ..database import get_db
from ..models.organization import OrgCreate, OrgOut, OrgUpdate
from ..services.templates import get_template, list_templates

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", status_code=201)
def create_organization(
    body: OrgCreate,
    user: Annotated[UserContext, Depends(get_user)],
):
    """
    Called once during onboarding. Creates the org keyed to the Clerk user.
    Idempotent — returns existing org if already created.
    """
    db = get_db()
    existing = (
        db.table("organizations")
        .select("*")
        .eq("clerk_user_id", user.user_id)
        .maybe_single()
        .execute()
    )
    if existing is not None and existing.data:
        return existing.data

    result = db.table("organizations").insert({
        "clerk_user_id": user.user_id,
        "clerk_org_id":  user.user_id,
        "name":          body.name,
        "industry":      body.industry,
        "city":          body.city,
        "state":         body.state,
    }).execute()
    return result.data[0]


@router.get("/me")
def get_my_org(auth: Annotated[AuthContext, Depends(get_auth)]):
    db = get_db()
    result = db.table("organizations").select("*").eq("id", auth.org_id).single().execute()
    return result.data


@router.patch("/me")
def update_my_org(
    body: OrgUpdate,
    auth: Annotated[AuthContext, Depends(get_auth)],
):
    db = get_db()
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")
    result = db.table("organizations").update(update_data).eq("id", auth.org_id).execute()
    return result.data[0]


@router.get("/templates")
def get_templates():
    return list_templates()


@router.get("/templates/{industry}")
def get_industry_template(industry: str):
    template = get_template(industry)
    if not template:
        raise HTTPException(status_code=404, detail=f"No template for industry '{industry}'")
    return template
