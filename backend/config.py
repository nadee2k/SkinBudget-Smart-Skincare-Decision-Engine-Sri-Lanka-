from functools import lru_cache
from typing import Annotated, List

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "SkinBudget API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    db_dsn: str = "postgresql://admin:password@localhost:5432/skinbudget"
    cors_origins: Annotated[List[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:8000", "http://127.0.0.1:8000"]
    )


    reco_concern_weight: float = 0.4
    reco_skin_weight: float = 0.2
    reco_rating_weight: float = 0.2
    reco_popularity_weight: float = 0.2

    @field_validator("reco_concern_weight", "reco_skin_weight", "reco_rating_weight", "reco_popularity_weight")
    @classmethod
    def validate_weight_range(cls, value: float):
        if value < 0 or value > 1:
            raise ValueError("Recommendation weights must be between 0 and 1")
        return value
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_weight_total(self):
        total = (
            self.reco_concern_weight
            + self.reco_skin_weight
            + self.reco_rating_weight
            + self.reco_popularity_weight
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError("Recommendation weights must add up to 1.0")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
