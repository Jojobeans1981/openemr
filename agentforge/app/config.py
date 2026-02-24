from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    google_api_key: str = ""
    model_name: str = "gemini-2.0-flash"
    model_temperature: float = 0.1
    model_max_tokens: int = 4096

    # OpenEMR
    openemr_base_url: str = "https://openemr"
    openemr_client_id: str = ""
    openemr_client_secret: str = ""

    # LangSmith
    langchain_tracing_v2: bool = True
    langchain_api_key: str = ""
    langchain_project: str = "agentforge-healthcare"

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
