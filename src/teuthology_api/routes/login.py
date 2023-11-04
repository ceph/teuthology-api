import logging
import os
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from teuthology_api.services.auth import get_github_auth_service, AuthService

load_dotenv()

GH_CLIENT_ID = os.getenv("GH_CLIENT_ID")
GH_AUTHORIZATION_BASE_URL = os.getenv("GH_AUTHORIZATION_BASE_URL")
PULPITO_URL = os.getenv("PULPITO_URL")

log = logging.getLogger(__name__)
router = APIRouter(
    prefix="/login",
    tags=["login"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=200)
async def github_login():
    """
    GET route for /login, (If first time) will redirect to github login page
    where you should authorize the app to gain access.
    """
    if not GH_AUTHORIZATION_BASE_URL or not GH_CLIENT_ID:
        return HTTPException(status_code=500, detail="Environment secrets are missing.")
    scope = "read:org"
    return RedirectResponse(
        f"{GH_AUTHORIZATION_BASE_URL}?client_id={GH_CLIENT_ID}&scope={scope}",
        status_code=302,
    )


@router.get("/callback", status_code=200)
async def handle_callback(code: str, request: Request, auth_service: AuthService = Depends(get_github_auth_service)):
    """
    Call back route after user login & authorize the app
    for access.
    """
    token = await auth_service._get_token(status_code=code)
    
    response_org_dict = await auth_service._get_org(token=token)
    
    data = {
            "id": response_org_dict.get("user", {}).get("id"),
            "username": response_org_dict.get("user", {}).get("login"),
            "state": response_org_dict.get("state"),
            "role": response_org_dict.get("role"),
            "access_token": token,
        }

    request.session["user"] = data

    cookie_data = {
        "username": data["username"],
        "avatar_url": response_org_dict.get("user", {}).get("avatar_url"),
    }
    cookie = "; ".join(
        [f"{str(key)}={str(value)}" for key, value in cookie_data.items()]
    )
    response = RedirectResponse(PULPITO_URL)
    response.set_cookie(key="GH_USER", value=cookie)
    return response
