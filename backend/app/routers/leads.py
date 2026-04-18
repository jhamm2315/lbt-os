from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import AuthContext, get_auth
from ..database import get_db
from ..models.lead import LeadCreate, LeadOut, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=list[LeadOut])
def list_leads(
    auth: Annotated[AuthContext, Depends(get_auth)],
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    db = get_db()
    query = (
        db.table("leads")
        .select("*")
        .eq("org_id", auth.org_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )
    if status:
        query = query.eq("status", status)
    if source:
        query = query.eq("source", source)

    return query.execute().data


@router.post("", response_model=LeadOut, status_code=201)
def create_lead(body: LeadCreate, auth: Annotated[AuthContext, Depends(get_auth)]):
    db = get_db()
    data = body.model_dump(exclude_none=True)
    data["org_id"] = auth.org_id
    result = db.table("leads").insert(data).execute()
    return result.data[0]


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: str, auth: Annotated[AuthContext, Depends(get_auth)]):
    db = get_db()
    result = (
        db.table("leads")
        .select("*")
        .eq("id", lead_id)
        .eq("org_id", auth.org_id)   # tenant isolation
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return result.data


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: str,
    body: LeadUpdate,
    auth: Annotated[AuthContext, Depends(get_auth)],
):
    db = get_db()
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")

    # Serialize datetimes to ISO strings for Supabase
    for k, v in update_data.items():
        if hasattr(v, "isoformat"):
            update_data[k] = v.isoformat()

    result = (
        db.table("leads")
        .update(update_data)
        .eq("id", lead_id)
        .eq("org_id", auth.org_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return result.data[0]


@router.delete("/{lead_id}", status_code=204)
def delete_lead(lead_id: str, auth: Annotated[AuthContext, Depends(get_auth)]):
    db = get_db()
    db.table("leads").delete().eq("id", lead_id).eq("org_id", auth.org_id).execute()


@router.post("/{lead_id}/convert", response_model=dict)
def convert_lead_to_customer(lead_id: str, auth: Annotated[AuthContext, Depends(get_auth)]):
    """
    Mark a lead as won and create a customer record.
    Returns the new customer.
    """
    from datetime import datetime, timezone
    db = get_db()

    lead = (
        db.table("leads")
        .select("*")
        .eq("id", lead_id)
        .eq("org_id", auth.org_id)
        .maybe_single()
        .execute()
    )
    if not lead.data:
        raise HTTPException(status_code=404, detail="Lead not found.")
    if lead.data["status"] == "won":
        raise HTTPException(status_code=400, detail="Lead already converted.")

    now = datetime.now(timezone.utc).isoformat()
    db.table("leads").update({"status": "won", "converted_at": now}).eq("id", lead_id).execute()

    customer = db.table("customers").insert({
        "org_id":  auth.org_id,
        "lead_id": lead_id,
        "name":    lead.data["name"],
        "email":   lead.data.get("email"),
        "phone":   lead.data.get("phone"),
    }).execute()

    return {"customer": customer.data[0]}
