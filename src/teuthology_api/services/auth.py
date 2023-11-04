import abc
import os
import httpx
import logging
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
log = logging.getLogger(__name__)

class AuthService(abc.ABC):
    @abc.abstractmethod
    async def _get_token(self, status_code: int) -> dict:
        """Returns a dict of response JSON from GH."""
        pass

    @abc.abstractmethod
    async def _get_org(self, token: str) -> dict:
        """Returns org info of user."""
        pass

class AuthServiceGH(AuthService):

    def __init__(self):
        self.GH_CLIENT_ID = os.getenv("GH_CLIENT_ID")
        self.GH_CLIENT_SECRET = os.getenv("GH_CLIENT_SECRET")
        self.GH_AUTHORIZATION_BASE_URL = os.getenv("GH_AUTHORIZATION_BASE_URL")
        self.GH_TOKEN_URL = os.getenv("GH_TOKEN_URL")
        self.GH_FETCH_MEMBERSHIP_URL = os.getenv("GH_FETCH_MEMBERSHIP_URL")
        self.PULPITO_URL = os.getenv("PULPITO_URL")

    async def _get_token(self, status_code: int) -> str:
        params = {
            "client_id": self.GH_CLIENT_ID,
            "client_secret": self.GH_CLIENT_SECRET,
            "code": status_code,
        }
        headers = {"Accept": "application/json"}
        async with httpx.AsyncClient as client:
            response_token = await client.post(
                url=self.GH_TOKEN_URL, params=params, headers=headers
            )
            log.info(response_token.json())
            response_token_dict = dict(response_token.json())
            token = response_token_dict.get("access_token")
            if response_token_dict.get("error") or not token:
                log.error("The code is incorrect or expired.")
                raise HTTPException(
                    status_code=401, detail="The code is incorrect or expired."
                )
            return token

    async def _get_org(self, token: str) -> dict:
        headers = {"Authorization": "token " + token}
        async with httpx.AsyncClient as client:
            response_org = await client.get(url=self.GH_FETCH_MEMBERSHIP_URL, headers=headers)
            response_org_dict = dict(response_org.json())
            log.info(response_org)
            if response_org.status_code == 404:
                log.error("User is not part of the Ceph Organization")
                raise HTTPException(
                    status_code=404,
                    detail="User is not part of the Ceph Organization, please contact <admin>.",
                )
            if response_org.status_code == 403:
                log.error("The application doesn't have permission to view github org.")
                raise HTTPException(
                    status_code=403,
                    detail="The application doesn't have permission to view github org.",
                )
            return response_org_dict

class AuthServiceMock(AuthService):
    pass

def get_github_auth_service():
    return AuthServiceGH()

def get_mock_auth_service():
    return AuthServiceMock()
