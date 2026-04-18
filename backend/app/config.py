from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase
    supabase_url: str
    supabase_service_key: str

    # Clerk
    clerk_secret_key: str
    clerk_publishable_key: str
    clerk_webhook_secret: str

    # LLM — supports OpenAI or Ollama
    # For Ollama: set llm_provider=ollama, ollama_model=llama3.2, leave openai_api_key empty
    # For OpenAI: set llm_provider=openai, openai_api_key=sk-...
    llm_provider: str = "ollama"          # "openai" | "ollama"
    openai_api_key: str = "not-needed"   # only required when llm_provider=openai
    openai_model: str = "gpt-4o-mini"    # used when llm_provider=openai
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"       # any model you have pulled

    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str
    stripe_price_basic: str
    stripe_price_pro: str
    stripe_price_premium: str

    # App
    app_env: str = "development"
    frontend_url: str = "http://localhost:5173"
    api_secret: str = "dev-secret"

    # Integration / OAuth
    integration_secret_key: Optional[str] = None
    quickbooks_client_id: Optional[str] = None
    quickbooks_client_secret: Optional[str] = None
    quickbooks_redirect_uri: Optional[str] = None
    hubspot_client_id: Optional[str] = None
    hubspot_client_secret: Optional[str] = None
    hubspot_redirect_uri: Optional[str] = None


settings = Settings()

PLAN_PRICE_MAP: dict[str, str] = {
    "basic":   settings.stripe_price_basic,
    "pro":     settings.stripe_price_pro,
    "premium": settings.stripe_price_premium,
}

PLAN_FEATURES: dict[str, list[str]] = {
    "basic":   ["leads", "sales", "customers", "expenses", "dashboard"],
    "pro":     ["leads", "sales", "customers", "expenses", "dashboard", "ai_audit"],
    "premium": ["leads", "sales", "customers", "expenses", "dashboard", "ai_audit", "consulting"],
}
