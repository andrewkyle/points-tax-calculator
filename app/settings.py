from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tax_year_url: str = (
        "http://localhost:5001/tax-calculator/tax-year/{tax_year}"
    )
    tax_year_retry: int = 3
    tax_year_timeout: int = 10

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
