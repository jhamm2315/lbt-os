from __future__ import annotations

import base64
import hmac
import hashlib
import json
from urllib.parse import urlencode
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

import httpx
from cryptography.fernet import Fernet
from fastapi import HTTPException
from supabase import Client

from ..config import settings


SUPPORTED_PROVIDERS: dict[str, dict[str, Any]] = {
    "quickbooks": {
        "key": "quickbooks",
        "label": "QuickBooks Online",
        "category": "accounting",
        "description": "Sync customers, invoices, and expenses from QuickBooks Online into LBT OS.",
        "required_credentials": ["access_token", "realm_id"],
        "oauth_supported": True,
        "schema_mapping": [
            {"raw_object": "Customer", "mapped_table": "customers", "key_fields": ["DisplayName", "PrimaryEmailAddr.Address", "PrimaryPhone.FreeFormNumber"]},
            {"raw_object": "Invoice", "mapped_table": "sales", "key_fields": ["TotalAmt", "TxnDate", "CustomerRef.value"]},
            {"raw_object": "Purchase", "mapped_table": "expenses", "key_fields": ["TotalAmt", "TxnDate", "AccountRef.name"]},
        ],
    },
    "hubspot": {
        "key": "hubspot",
        "label": "HubSpot CRM",
        "category": "crm",
        "description": "Sync contacts and deals from HubSpot so audits can read pipeline activity automatically.",
        "required_credentials": ["access_token"],
        "oauth_supported": True,
        "schema_mapping": [
            {"raw_object": "contacts", "mapped_table": "leads", "key_fields": ["firstname", "lastname", "email", "phone"]},
            {"raw_object": "deals", "mapped_table": "leads/sales", "key_fields": ["dealname", "amount", "dealstage", "closedate"]},
        ],
    },
}

EXPENSE_CATEGORY_KEYWORDS = {
    "payroll": "payroll",
    "labor": "payroll",
    "materials": "materials",
    "supply": "materials",
    "marketing": "marketing",
    "ads": "marketing",
    "rent": "rent",
    "lease": "rent",
    "utilities": "utilities",
    "electric": "utilities",
    "software": "software",
    "saas": "software",
    "insurance": "insurance",
    "equipment": "equipment",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fernet() -> Fernet:
    secret = settings.integration_secret_key or settings.api_secret
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def _encrypt_credentials(credentials: dict[str, Any]) -> str:
    payload = json.dumps(credentials).encode("utf-8")
    return _fernet().encrypt(payload).decode("utf-8")


def _decrypt_credentials(ciphertext: str | None) -> dict[str, Any]:
    if not ciphertext:
        return {}
    raw = _fernet().decrypt(ciphertext.encode("utf-8"))
    return json.loads(raw.decode("utf-8"))


def _normalize_expense_category(value: str | None) -> str:
    if not value:
        return "misc"
    normalized = value.strip().lower()
    for keyword, category in EXPENSE_CATEGORY_KEYWORDS.items():
        if keyword in normalized:
            return category
    return "misc"


def list_provider_definitions() -> list[dict[str, Any]]:
    definitions = []
    for provider in SUPPORTED_PROVIDERS.values():
        item = dict(provider)
        item.pop("required_credentials", None)
        definitions.append(item)
    return definitions


def _sign_value(raw: str) -> str:
    secret = (settings.integration_secret_key or settings.api_secret).encode("utf-8")
    return hmac.new(secret, raw.encode("utf-8"), hashlib.sha256).hexdigest()


def build_oauth_state(org_id: str, provider: str) -> str:
    payload = {"org_id": org_id, "provider": provider, "ts": int(datetime.now(timezone.utc).timestamp())}
    raw = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    return f"{raw}.{_sign_value(raw)}"


def parse_oauth_state(state: str) -> dict[str, Any]:
    try:
        raw, signature = state.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid OAuth state.") from exc
    if not hmac.compare_digest(signature, _sign_value(raw)):
        raise HTTPException(status_code=400, detail="OAuth state signature mismatch.")
    payload = json.loads(base64.urlsafe_b64decode(raw.encode("utf-8")).decode("utf-8"))
    if datetime.now(timezone.utc).timestamp() - int(payload["ts"]) > 900:
        raise HTTPException(status_code=400, detail="OAuth state expired.")
    return payload


def get_frontend_connection_callback(provider: str, status: str, message: str | None = None) -> str:
    query = {"provider": provider, "status": status}
    if message:
        query["message"] = message
    return f"{settings.frontend_url}/app/connections?{urlencode(query)}"


def get_oauth_authorization_url(provider: str, org_id: str) -> str:
    state = build_oauth_state(org_id, provider)
    if provider == "quickbooks":
        if not settings.quickbooks_client_id or not settings.quickbooks_redirect_uri:
            raise HTTPException(status_code=500, detail="QuickBooks OAuth is not configured.")
        params = {
            "client_id": settings.quickbooks_client_id,
            "response_type": "code",
            "scope": "com.intuit.quickbooks.accounting",
            "redirect_uri": settings.quickbooks_redirect_uri,
            "state": state,
        }
        return f"https://appcenter.intuit.com/connect/oauth2?{urlencode(params)}"

    if provider == "hubspot":
        if not settings.hubspot_client_id or not settings.hubspot_redirect_uri:
            raise HTTPException(status_code=500, detail="HubSpot OAuth is not configured.")
        params = {
            "client_id": settings.hubspot_client_id,
            "redirect_uri": settings.hubspot_redirect_uri,
            "scope": "oauth crm.objects.contacts.read crm.objects.deals.read",
            "state": state,
        }
        return f"https://app.hubspot.com/oauth/authorize?{urlencode(params)}"

    raise HTTPException(status_code=400, detail=f"Unsupported provider '{provider}'.")


def list_connections(db: Client, org_id: str) -> list[dict[str, Any]]:
    result = (
        db.table("integration_connections")
        .select("id, org_id, provider, label, status, config, external_account_id, external_account_name, last_synced_at, last_sync_status, last_sync_error, created_at, updated_at")
        .eq("org_id", org_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def list_sync_runs(db: Client, org_id: str, limit: int = 20) -> list[dict[str, Any]]:
    result = (
        db.table("integration_sync_runs")
        .select("*")
        .eq("org_id", org_id)
        .order("started_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def get_connection(db: Client, org_id: str, connection_id: str) -> dict[str, Any]:
    result = (
        db.table("integration_connections")
        .select("*")
        .eq("org_id", org_id)
        .eq("id", connection_id)
        .maybe_single()
        .execute()
    )
    if result is None or not result.data:
        raise HTTPException(status_code=404, detail="Integration connection not found.")
    return result.data


def create_connection(
    db: Client,
    org_id: str,
    provider: str,
    credentials: dict[str, Any],
    config: dict[str, Any] | None = None,
    label: str | None = None,
    external_account_id: str | None = None,
    external_account_name: str | None = None,
) -> dict[str, Any]:
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider '{provider}'.")

    required = SUPPORTED_PROVIDERS[provider]["required_credentials"]
    missing = [key for key in required if not credentials.get(key)]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required credentials: {', '.join(missing)}")

    payload = {
        "org_id": org_id,
        "provider": provider,
        "label": label or SUPPORTED_PROVIDERS[provider]["label"],
        "status": "connected",
        "credentials_encrypted": _encrypt_credentials(credentials),
        "config": config or {},
        "external_account_id": external_account_id,
        "external_account_name": external_account_name,
    }
    result = db.table("integration_connections").insert(payload).execute()
    connection_id = result.data[0]["id"]
    return sanitize_connection(get_connection(db, org_id, connection_id))


def update_connection(
    db: Client,
    org_id: str,
    connection_id: str,
    *,
    label: str | None = None,
    credentials: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
    status: str | None = None,
    external_account_id: str | None = None,
    external_account_name: str | None = None,
) -> dict[str, Any]:
    existing = get_connection(db, org_id, connection_id)
    update_data: dict[str, Any] = {}
    if label is not None:
        update_data["label"] = label
    if config is not None:
        update_data["config"] = config
    if status is not None:
        update_data["status"] = status
    if external_account_id is not None:
        update_data["external_account_id"] = external_account_id
    if external_account_name is not None:
        update_data["external_account_name"] = external_account_name
    if credentials is not None:
        merged = _decrypt_credentials(existing.get("credentials_encrypted"))
        merged.update(credentials)
        update_data["credentials_encrypted"] = _encrypt_credentials(merged)
    if not update_data:
        return sanitize_connection(existing)
    result = (
        db.table("integration_connections")
        .update(update_data)
        .eq("id", connection_id)
        .eq("org_id", org_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Integration connection not found.")
    return sanitize_connection(get_connection(db, org_id, connection_id))


def sanitize_connection(connection: dict[str, Any]) -> dict[str, Any]:
    safe = dict(connection)
    safe.pop("credentials_encrypted", None)
    return safe


def _find_connection_by_provider(db: Client, org_id: str, provider: str) -> dict[str, Any] | None:
    result = (
        db.table("integration_connections")
        .select("*")
        .eq("org_id", org_id)
        .eq("provider", provider)
        .maybe_single()
        .execute()
    )
    if result is None:
        return None
    return result.data


def upsert_oauth_connection(
    db: Client,
    *,
    org_id: str,
    provider: str,
    credentials: dict[str, Any],
    config: dict[str, Any] | None = None,
    external_account_id: str | None = None,
    external_account_name: str | None = None,
) -> dict[str, Any]:
    existing = _find_connection_by_provider(db, org_id, provider)
    if existing:
        return update_connection(
            db,
            org_id,
            existing["id"],
            credentials=credentials,
            config={**(existing.get("config") or {}), **(config or {})},
            status="connected",
            external_account_id=external_account_id or existing.get("external_account_id"),
            external_account_name=external_account_name or existing.get("external_account_name"),
        )
    return create_connection(
        db,
        org_id,
        provider=provider,
        credentials=credentials,
        config=config or {},
        label=SUPPORTED_PROVIDERS[provider]["label"],
        external_account_id=external_account_id,
        external_account_name=external_account_name,
    )


def exchange_oauth_code(db: Client, provider: str, code: str, state: str, extra_query: dict[str, Any]) -> dict[str, Any]:
    payload = parse_oauth_state(state)
    org_id = payload["org_id"]
    if payload["provider"] != provider:
        raise HTTPException(status_code=400, detail="OAuth provider mismatch.")

    if provider == "quickbooks":
        token_response = httpx.post(
            "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
            auth=(settings.quickbooks_client_id or "", settings.quickbooks_client_secret or ""),
            headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.quickbooks_redirect_uri or "",
            },
            timeout=20,
        )
        token_response.raise_for_status()
        token_payload = token_response.json()
        credentials = {
            "access_token": token_payload["access_token"],
            "refresh_token": token_payload.get("refresh_token"),
            "realm_id": extra_query.get("realmId"),
            "token_type": token_payload.get("token_type"),
            "expires_at": int(datetime.now(timezone.utc).timestamp()) + int(token_payload.get("expires_in", 3600)),
            "refresh_expires_in": token_payload.get("x_refresh_token_expires_in"),
        }
        connection = upsert_oauth_connection(
            db,
            org_id=org_id,
            provider=provider,
            credentials=credentials,
            external_account_id=extra_query.get("realmId"),
            external_account_name=f"QuickBooks Company {extra_query.get('realmId')}" if extra_query.get("realmId") else None,
        )
        return connection

    if provider == "hubspot":
        token_response = httpx.post(
            "https://api.hubapi.com/oauth/v3/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "client_id": settings.hubspot_client_id or "",
                "client_secret": settings.hubspot_client_secret or "",
                "redirect_uri": settings.hubspot_redirect_uri or "",
                "code": code,
            },
            timeout=20,
        )
        token_response.raise_for_status()
        token_payload = token_response.json()
        credentials = {
            "access_token": token_payload["access_token"],
            "refresh_token": token_payload.get("refresh_token"),
            "hub_id": token_payload.get("hub_id"),
            "scopes": token_payload.get("scopes", []),
            "expires_at": int(datetime.now(timezone.utc).timestamp()) + int(token_payload.get("expires_in", 1800)),
        }
        connection = upsert_oauth_connection(
            db,
            org_id=org_id,
            provider=provider,
            credentials=credentials,
            external_account_id=str(token_payload.get("hub_id")) if token_payload.get("hub_id") else None,
            external_account_name=f"HubSpot Portal {token_payload.get('hub_id')}" if token_payload.get("hub_id") else None,
        )
        return connection

    raise HTTPException(status_code=400, detail=f"Unsupported provider '{provider}'.")


def _refresh_provider_credentials(provider: str, credentials: dict[str, Any]) -> dict[str, Any]:
    now_ts = int(datetime.now(timezone.utc).timestamp())
    if credentials.get("expires_at") and int(credentials["expires_at"]) - now_ts > 120:
        return credentials

    if provider == "quickbooks" and credentials.get("refresh_token"):
        response = httpx.post(
            "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
            auth=(settings.quickbooks_client_id or "", settings.quickbooks_client_secret or ""),
            headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "refresh_token",
                "refresh_token": credentials["refresh_token"],
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        credentials.update({
            "access_token": payload["access_token"],
            "refresh_token": payload.get("refresh_token", credentials["refresh_token"]),
            "expires_at": now_ts + int(payload.get("expires_in", 3600)),
            "refresh_expires_in": payload.get("x_refresh_token_expires_in", credentials.get("refresh_expires_in")),
        })
        return credentials

    if provider == "hubspot" and credentials.get("refresh_token"):
        response = httpx.post(
            "https://api.hubapi.com/oauth/v3/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "refresh_token",
                "client_id": settings.hubspot_client_id or "",
                "client_secret": settings.hubspot_client_secret or "",
                "redirect_uri": settings.hubspot_redirect_uri or "",
                "refresh_token": credentials["refresh_token"],
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        credentials.update({
            "access_token": payload["access_token"],
            "refresh_token": payload.get("refresh_token", credentials["refresh_token"]),
            "expires_at": now_ts + int(payload.get("expires_in", 1800)),
        })
        return credentials

    return credentials


def _record_sync_run_start(db: Client, connection: dict[str, Any], trigger_source: str) -> dict[str, Any]:
    result = db.table("integration_sync_runs").insert({
        "org_id": connection["org_id"],
        "connection_id": connection["id"],
        "provider": connection["provider"],
        "trigger_source": trigger_source,
        "status": "running",
        "stats": {},
        "started_at": _utc_now(),
    }).execute()
    return result.data[0]


def _record_sync_run_finish(
    db: Client,
    connection: dict[str, Any],
    run_id: str,
    *,
    status: str,
    stats: dict[str, Any],
    error: str | None = None,
) -> dict[str, Any]:
    finished_at = _utc_now()
    db.table("integration_sync_runs").update({
        "status": status,
        "stats": stats,
        "error": error,
        "finished_at": finished_at,
    }).eq("id", run_id).execute()
    db.table("integration_connections").update({
        "last_synced_at": finished_at,
        "last_sync_status": status,
        "last_sync_error": error,
        "status": "connected" if status in {"success", "partial"} else "error",
    }).eq("id", connection["id"]).execute()
    return (
        db.table("integration_sync_runs")
        .select("*")
        .eq("id", run_id)
        .single()
        .execute()
        .data
    )


def _get_record_link(
    db: Client,
    connection_id: str,
    object_type: str,
    external_id: str,
) -> dict[str, Any] | None:
    result = (
        db.table("integration_record_links")
        .select("*")
        .eq("connection_id", connection_id)
        .eq("object_type", object_type)
        .eq("external_id", external_id)
        .maybe_single()
        .execute()
    )
    if result is None:
        return None
    return result.data


def _upsert_record_link(
    db: Client,
    *,
    org_id: str,
    connection_id: str,
    provider: str,
    object_type: str,
    external_id: str,
    local_table: str,
    local_id: str,
    fingerprint: str | None = None,
) -> None:
    existing = _get_record_link(db, connection_id, object_type, external_id)
    payload = {
        "org_id": org_id,
        "connection_id": connection_id,
        "provider": provider,
        "object_type": object_type,
        "external_id": external_id,
        "local_table": local_table,
        "local_id": local_id,
        "fingerprint": fingerprint,
        "last_seen_at": _utc_now(),
    }
    if existing:
        db.table("integration_record_links").update(payload).eq("id", existing["id"]).execute()
    else:
        db.table("integration_record_links").insert(payload).execute()


def _upsert_local_row(
    db: Client,
    *,
    org_id: str,
    table: str,
    connection: dict[str, Any],
    object_type: str,
    external_id: str,
    payload: dict[str, Any],
    fingerprint: str | None = None,
) -> str:
    link = _get_record_link(db, connection["id"], object_type, external_id)
    if link:
        db.table(table).update(payload).eq("id", link["local_id"]).eq("org_id", org_id).execute()
        local_id = link["local_id"]
    else:
        insert_result = db.table(table).insert({"org_id": org_id, **payload}).execute()
        local_id = insert_result.data[0]["id"]
    _upsert_record_link(
        db,
        org_id=org_id,
        connection_id=connection["id"],
        provider=connection["provider"],
        object_type=object_type,
        external_id=external_id,
        local_table=table,
        local_id=local_id,
        fingerprint=fingerprint,
    )
    return local_id


def _customer_link_from_external(
    db: Client,
    connection_id: str,
    object_type: str,
    external_id: str | None,
) -> str | None:
    if not external_id:
        return None
    link = _get_record_link(db, connection_id, object_type, external_id)
    if not link:
        return None
    return link["local_id"]


@dataclass
class BaseProvider:
    provider_key: str

    def sync(self, db: Client, connection: dict[str, Any], credentials: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class QuickBooksProvider(BaseProvider):
    provider_key = "quickbooks"

    def _base_url(self, credentials: dict[str, Any], endpoint: str) -> str:
        realm_id = credentials["realm_id"]
        sandbox = bool(credentials.get("sandbox"))
        host = "https://sandbox-quickbooks.api.intuit.com" if sandbox else "https://quickbooks.api.intuit.com"
        return f"{host}/v3/company/{realm_id}/{endpoint}"

    def _query(self, credentials: dict[str, Any], query: str) -> dict[str, Any]:
        response = httpx.get(
            self._base_url(credentials, "query"),
            headers={
                "Authorization": f"Bearer {credentials['access_token']}",
                "Accept": "application/json",
            },
            params={"query": query, "minorversion": credentials.get("minorversion", 75)},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def _fetch_entities(self, credentials: dict[str, Any], entity: str) -> list[dict[str, Any]]:
        payload = self._query(credentials, f"select * from {entity} maxresults 1000")
        return payload.get("QueryResponse", {}).get(entity, []) or []

    def sync(self, db: Client, connection: dict[str, Any], credentials: dict[str, Any]) -> dict[str, Any]:
        customers = self._fetch_entities(credentials, "Customer")
        invoices = self._fetch_entities(credentials, "Invoice")
        purchases = self._fetch_entities(credentials, "Purchase")

        stats = {"customers": 0, "sales": 0, "expenses": 0}

        for customer in customers:
            display_name = customer.get("DisplayName") or customer.get("CompanyName") or customer.get("FullyQualifiedName")
            if not display_name:
                continue
            local_id = _upsert_local_row(
                db,
                org_id=connection["org_id"],
                table="customers",
                connection=connection,
                object_type="customer",
                external_id=str(customer["Id"]),
                payload={
                    "name": display_name,
                    "email": (customer.get("PrimaryEmailAddr") or {}).get("Address"),
                    "phone": (customer.get("PrimaryPhone") or {}).get("FreeFormNumber"),
                    "address": ", ".join(filter(None, [
                        (customer.get("BillAddr") or {}).get("Line1"),
                        (customer.get("BillAddr") or {}).get("City"),
                        (customer.get("BillAddr") or {}).get("CountrySubDivisionCode"),
                    ])) or None,
                    "notes": "Imported from QuickBooks Online.",
                },
                fingerprint=customer.get("SyncToken"),
            )
            stats["customers"] += 1 if local_id else 0

        for invoice in invoices:
            total = float(invoice.get("TotalAmt") or 0)
            if total <= 0:
                continue
            customer_id = _customer_link_from_external(
                db,
                connection["id"],
                "customer",
                (invoice.get("CustomerRef") or {}).get("value"),
            )
            first_line = (invoice.get("Line") or [{}])[0] or {}
            sold_at = invoice.get("TxnDate")
            if sold_at:
                sold_at = f"{sold_at}T00:00:00+00:00"
            _upsert_local_row(
                db,
                org_id=connection["org_id"],
                table="sales",
                connection=connection,
                object_type="invoice",
                external_id=str(invoice["Id"]),
                payload={
                    "customer_id": customer_id,
                    "service": first_line.get("Description") or invoice.get("DocNumber") or "QuickBooks Invoice",
                    "amount": total,
                    "cost": 0,
                    "payment_method": "bank_transfer",
                    "payment_status": "paid" if float(invoice.get("Balance") or 0) <= 0 else "pending",
                    "source": "quickbooks",
                    "invoice_number": invoice.get("DocNumber"),
                    "notes": "Imported from QuickBooks Online invoice.",
                    "sold_at": sold_at or _utc_now(),
                },
                fingerprint=invoice.get("SyncToken"),
            )
            stats["sales"] += 1

        for purchase in purchases:
            total = float(purchase.get("TotalAmt") or 0)
            if total <= 0:
                continue
            expense_date = purchase.get("TxnDate") or date.today().isoformat()
            vendor = (purchase.get("EntityRef") or {}).get("name")
            description = (purchase.get("PrivateNote") or purchase.get("DocNumber") or "QuickBooks expense").strip()
            account_name = (purchase.get("AccountRef") or {}).get("name") or description
            _upsert_local_row(
                db,
                org_id=connection["org_id"],
                table="expenses",
                connection=connection,
                object_type="purchase",
                external_id=str(purchase["Id"]),
                payload={
                    "category": _normalize_expense_category(account_name),
                    "description": description[:200],
                    "amount": total,
                    "vendor": vendor,
                    "is_recurring": False,
                    "expense_date": expense_date,
                },
                fingerprint=purchase.get("SyncToken"),
            )
            stats["expenses"] += 1

        return stats


class HubSpotProvider(BaseProvider):
    provider_key = "hubspot"

    def _get(self, credentials: dict[str, Any], path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = httpx.get(
            f"https://api.hubapi.com{path}",
            headers={"Authorization": f"Bearer {credentials['access_token']}"},
            params=params or {},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def _fetch_objects(self, credentials: dict[str, Any], object_type: str, properties: list[str]) -> list[dict[str, Any]]:
        after = None
        results: list[dict[str, Any]] = []
        while True:
            params: dict[str, Any] = {"limit": 100, "properties": ",".join(properties)}
            if after:
                params["after"] = after
            payload = self._get(credentials, f"/crm/v3/objects/{object_type}", params=params)
            results.extend(payload.get("results", []))
            after = payload.get("paging", {}).get("next", {}).get("after")
            if not after:
                break
        return results

    def _map_hubspot_status(self, dealstage: str | None) -> str:
        if not dealstage:
            return "new"
        stage = dealstage.lower()
        if "won" in stage:
            return "won"
        if "lost" in stage:
            return "lost"
        if "proposal" in stage or "quote" in stage:
            return "proposal"
        if "qualified" in stage:
            return "qualified"
        if "contact" in stage:
            return "contacted"
        return "new"

    def sync(self, db: Client, connection: dict[str, Any], credentials: dict[str, Any]) -> dict[str, Any]:
        contacts = self._fetch_objects(credentials, "contacts", ["firstname", "lastname", "email", "phone", "hs_analytics_source", "lifecyclestage"])
        deals = self._fetch_objects(credentials, "deals", ["dealname", "amount", "dealstage", "closedate", "pipeline", "hs_analytics_source"])
        stats = {"leads": 0, "sales": 0}

        for contact in contacts:
            props = contact.get("properties", {})
            full_name = " ".join(filter(None, [props.get("firstname"), props.get("lastname")])).strip() or props.get("email") or f"HubSpot Contact {contact['id']}"
            _upsert_local_row(
                db,
                org_id=connection["org_id"],
                table="leads",
                connection=connection,
                object_type="contact",
                external_id=str(contact["id"]),
                payload={
                    "name": full_name,
                    "email": props.get("email"),
                    "phone": props.get("phone"),
                    "source": (props.get("hs_analytics_source") or "website").lower()[:20],
                    "status": "new",
                    "notes": "Imported from HubSpot contact.",
                },
                fingerprint=contact.get("updatedAt"),
            )
            stats["leads"] += 1

        for deal in deals:
            props = deal.get("properties", {})
            status = self._map_hubspot_status(props.get("dealstage"))
            amount = float(props.get("amount") or 0)
            close_date = props.get("closedate")
            close_ts = close_date or _utc_now()
            if close_ts and close_ts.endswith("Z") is False and "T" in close_ts:
                close_ts = close_ts + "Z"
            if status == "won" and amount > 0:
                _upsert_local_row(
                    db,
                    org_id=connection["org_id"],
                    table="sales",
                    connection=connection,
                    object_type="deal_sale",
                    external_id=str(deal["id"]),
                    payload={
                        "service": props.get("dealname") or "HubSpot Deal",
                        "amount": amount,
                        "cost": 0,
                        "payment_status": "paid",
                        "source": (props.get("hs_analytics_source") or "hubspot").lower()[:20],
                        "invoice_number": str(deal["id"]),
                        "notes": "Imported from HubSpot closed-won deal.",
                        "sold_at": close_ts,
                    },
                    fingerprint=deal.get("updatedAt"),
                )
                stats["sales"] += 1
            else:
                _upsert_local_row(
                    db,
                    org_id=connection["org_id"],
                    table="leads",
                    connection=connection,
                    object_type="deal_lead",
                    external_id=str(deal["id"]),
                    payload={
                        "name": props.get("dealname") or f"HubSpot Deal {deal['id']}",
                        "source": (props.get("hs_analytics_source") or "hubspot").lower()[:20],
                        "status": status,
                        "estimated_value": amount if amount > 0 else None,
                        "notes": "Imported from HubSpot deal.",
                    },
                    fingerprint=deal.get("updatedAt"),
                )
                stats["leads"] += 1

        return stats


PROVIDER_REGISTRY: dict[str, BaseProvider] = {
    "quickbooks": QuickBooksProvider("quickbooks"),
    "hubspot": HubSpotProvider("hubspot"),
}


def run_connection_sync(
    db: Client,
    org_id: str,
    connection_id: str,
    *,
    trigger_source: str = "manual",
) -> dict[str, Any]:
    connection = get_connection(db, org_id, connection_id)
    provider = PROVIDER_REGISTRY.get(connection["provider"])
    if provider is None:
        raise HTTPException(status_code=400, detail=f"No sync provider registered for '{connection['provider']}'.")
    credentials = _decrypt_credentials(connection.get("credentials_encrypted"))
    credentials = _refresh_provider_credentials(connection["provider"], credentials)
    db.table("integration_connections").update({
        "credentials_encrypted": _encrypt_credentials(credentials),
    }).eq("id", connection["id"]).execute()
    sync_run = _record_sync_run_start(db, connection, trigger_source)
    try:
        stats = provider.sync(db, connection, credentials)
        status = "success" if stats else "partial"
        return _record_sync_run_finish(db, connection, sync_run["id"], status=status, stats=stats)
    except httpx.HTTPStatusError as exc:
        detail = f"{exc.response.status_code} {exc.response.text[:500]}"
        return _record_sync_run_finish(db, connection, sync_run["id"], status="failed", stats={}, error=detail)
    except Exception as exc:
        return _record_sync_run_finish(db, connection, sync_run["id"], status="failed", stats={}, error=str(exc))


def sync_all_connections_for_org(db: Client, org_id: str, *, trigger_source: str = "manual") -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for connection in list_connections(db, org_id):
        if connection.get("status") == "disconnected":
            continue
        runs.append(run_connection_sync(db, org_id, connection["id"], trigger_source=trigger_source))
    return runs
