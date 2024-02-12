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
    path_to_teuthology: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    # TODO: team names need to be changed below when created
    admin_team: str = "ceph"  # ceph's github team with *sudo* access to sepia
    teuth_team: str = "teuth"  # ceph's github team with access to sepia


@lru_cache()
def get_api_settings() -> APISettings:
    """
    Returns the API settings.
    """
    return APISettings()  # reads variables from environment


settings = get_api_settings()
