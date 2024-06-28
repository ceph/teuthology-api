from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class APISettings(BaseSettings):
    """
    Class for API settings.
    """

    deployment: str = ""
    pulpito_url: str = ""
    paddles_url: str = ""

    gh_client_id: str = ""
    gh_client_secret: str = ""
    gh_token_url: str = ""
    gh_authorization_base_url: str = ""
    gh_fetch_membership_url: str = ""

    session_secret_key: str = ""
    archive_dir: str = ""
    teuthology_path: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    admin_team: str = "Ceph"  # ceph's github team with *sudo* access to sepia


@lru_cache()
def get_api_settings() -> APISettings:
    """
    Returns the API settings.
    """
    return APISettings()  # reads variables from environment


settings = get_api_settings()
