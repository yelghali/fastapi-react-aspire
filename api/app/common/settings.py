"""Application settings using Pydantic BaseSettings.

Environment variables are loaded with the APP_ prefix.
Example: APP_DATABASE_CONNECTION -> settings.database_connection
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    All settings use the APP_ prefix. For example:
    - APP_DATABASE_CONNECTION -> database_connection
    - APP_STORAGE_CONNECTION -> storage_connection

    Extend this class to add more configuration options as needed.
    """

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_prefix="APP_",
    )

    # Database settings (for future Azure Cosmos DB integration)
    database_connection: str = Field(
        default="",
        description="Database connection string (e.g., Azure Cosmos DB)",
    )
    database_name: str = Field(
        default="StarterDB",
        description="Database name",
    )

    # Storage settings (for future Azure Storage integration)
    storage_connection: str = Field(
        default="",
        description="Storage connection string (e.g., Azure Blob Storage)",
    )
    storage_container: str = Field(
        default="",
        description="Storage container name",
    )

    # AI settings (for future Azure AI Foundry integration)
    foundry_endpoint: str = Field(
        default="",
        description="Azure AI Foundry project endpoint",
    )
    azure_openai_endpoint: str = Field(
        default="",
        description="Azure OpenAI endpoint for AI features",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


if __name__ == "__main__":
    # Quick test to print current settings
    settings = Settings()
    print(settings.model_dump())
