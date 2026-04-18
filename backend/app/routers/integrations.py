from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from ..auth import AuthContext, get_auth
from ..database import get_db
from ..models.integration import (
    IntegrationConnectionCreate,
    IntegrationConnectionOut,
    IntegrationConnectionUpdate,
    IntegrationSyncRunOut,
)
from ..services.integrations import (
    exchange_oauth_code,
    get_frontend_connection_callback,
    get_oauth_authorization_url,
    create_connection,
    get_connection,
    list_connections,
    list_provider_definitions,
    list_sync_runs,
    run_connection_sync,
    sanitize_connection,
    sync_all_connections_for_org,
    update_connection,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("/providers")
def providers():
    return list_provider_definitions()


@router.post("/oauth/{provider}/start")
def oauth_start(provider: str, auth: Annotated[AuthContext, Depends(get_auth)]):
    return {"authorization_url": get_oauth_authorization_url(provider, auth.org_id)}


@router.get("/oauth/{provider}/callback", include_in_schema=False)
def oauth_callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    realmId: str | None = None,
):
    if error:
        return RedirectResponse(get_frontend_connection_callback(provider, "error", error_description or error))
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state.")
    db = get_db()
    try:
        exchange_oauth_code(db, provider, code, state, {"realmId": realmId})
    except Exception as exc:
        return RedirectResponse(get_frontend_connection_callback(provider, "error", str(exc)))
    return RedirectResponse(get_frontend_connection_callback(provider, "connected"))


@router.get("/connections", response_model=list[IntegrationConnectionOut])
def connections(auth: Annotated[AuthContext, Depends(get_auth)]):
    db = get_db()
    return [sanitize_connection(row) for row in list_connections(db, auth.org_id)]


@router.post("/connections", response_model=IntegrationConnectionOut, status_code=201)
def add_connection(
    body: IntegrationConnectionCreate,
    auth: Annotated[AuthContext, Depends(get_auth)],
):
    db = get_db()
    return create_connection(
        db,
        auth.org_id,
        provider=body.provider,
        credentials=body.credentials,
        config=body.config,
        label=body.label,
        external_account_id=body.external_account_id,
        external_account_name=body.external_account_name,
    )


@router.patch("/connections/{connection_id}", response_model=IntegrationConnectionOut)
def patch_connection(
    connection_id: str,
    body: IntegrationConnectionUpdate,
    auth: Annotated[AuthContext, Depends(get_auth)],
):
    db = get_db()
    return update_connection(
        db,
        auth.org_id,
        connection_id,
        label=body.label,
        credentials=body.credentials,
        config=body.config,
        status=body.status,
        external_account_id=body.external_account_id,
        external_account_name=body.external_account_name,
    )


@router.get("/connections/{connection_id}", response_model=IntegrationConnectionOut)
def connection_detail(connection_id: str, auth: Annotated[AuthContext, Depends(get_auth)]):
    db = get_db()
    return sanitize_connection(get_connection(db, auth.org_id, connection_id))


@router.post("/connections/{connection_id}/sync", response_model=IntegrationSyncRunOut)
def sync_connection(connection_id: str, auth: Annotated[AuthContext, Depends(get_auth)]):
    db = get_db()
    return run_connection_sync(db, auth.org_id, connection_id, trigger_source="manual")


@router.post("/sync-all", response_model=list[IntegrationSyncRunOut])
def sync_all(auth: Annotated[AuthContext, Depends(get_auth)]):
    db = get_db()
    return sync_all_connections_for_org(db, auth.org_id, trigger_source="manual")


@router.get("/sync-runs", response_model=list[IntegrationSyncRunOut])
def sync_runs(
    auth: Annotated[AuthContext, Depends(get_auth)],
    limit: int = Query(20, ge=1, le=100),
):
    db = get_db()
    return list_sync_runs(db, auth.org_id, limit=limit)
