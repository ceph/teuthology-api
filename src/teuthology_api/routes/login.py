import logging
import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import httpx

load_dotenv()

GH_CLIENT_ID = os.getenv("GH_CLIENT_ID")
GH_CLIENT_SECRET = os.getenv("GH_CLIENT_SECRET")
GH_AUTHORIZATION_BASE_URL = os.getenv("GH_AUTHORIZATION_BASE_URL")
GH_TOKEN_URL = os.getenv("GH_TOKEN_URL")
GH_DEVICE_CODE_URL = os.getenv(
    "GH_DEVICE_CODE_URL", "https://github.com/login/device/code"
)
GH_FETCH_MEMBERSHIP_URL = os.getenv("GH_FETCH_MEMBERSHIP_URL")
PULPITO_URL = os.getenv("PULPITO_URL")

# Scope for device flow (must include read:org for Ceph org membership check)
DEVICE_FLOW_SCOPE = "read:org"

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
async def handle_callback(code: str, request: Request):
    """
    Call back route after user login & authorize the app
    for access.
    """
    params = {
        "client_id": GH_CLIENT_ID,
        "client_secret": GH_CLIENT_SECRET,
        "code": code,
    }
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        response_token = await client.post(
            url=GH_TOKEN_URL, params=params, headers=headers
        )
        log.info(response_token.json())
        response_token_dic = dict(response_token.json())
        token = response_token_dic.get("access_token")
        if response_token_dic.get("error") or not token:
            log.error("The code is incorrect or expired.")
            raise HTTPException(
                status_code=401, detail="The code is incorrect or expired."
            )
        headers = {"Authorization": "token " + token}
        response_org = await client.get(url=GH_FETCH_MEMBERSHIP_URL, headers=headers)
        log.info(response_org.json())
        if response_org.status_code == 404:
            log.error("User is not part of the Ceph Organization")
            raise HTTPException(
                status_code=404,
                detail="User is not part of the Ceph Organization, please contact <admin>",
            )
        if response_org.status_code == 403:
            log.error("The application doesn't have permission to view github org")
            raise HTTPException(
                status_code=403,
                detail="The application doesn't have permission to view github org",
            )
        response_org_dic = dict(response_org.json())
        data = {
            "id": response_org_dic.get("user", {}).get("id"),
            "username": response_org_dic.get("user", {}).get("login"),
            "avatar_url": response_org_dic.get("user", {}).get("avatar_url"),
            "state": response_org_dic.get("state"),
            "role": response_org_dic.get("role"),
            "access_token": token,
        }
        request.session["user"] = data
        from teuthology_api.services.helpers import isAdmin
        isUserAdmin = await isAdmin(data["username"], data["access_token"])
        data["isUserAdmin"] = isUserAdmin
    cookie_data = {
        "username": data["username"],
        "avatar_url": response_org_dic.get("user", {}).get("avatar_url"),
        "isUserAdmin": isUserAdmin,
    }
    cookie = "; ".join(
        [f"{str(key)}={str(value)}" for key, value in cookie_data.items()]
    )
    response = RedirectResponse(PULPITO_URL)
    response.set_cookie(key="GH_USER", value=cookie)
    return response


# --- Device flow (headless / CLI / scripts) ---


@router.post("/device/code", status_code=200)
async def device_code():
    """
    Start GitHub device flow. Returns device_code, user_code, verification_uri,
    expires_in, and interval. The client should show the user the verification_uri
    and user_code, then poll POST /login/device/token with the device_code until
    the user authorizes or the code expires.
    """
    if not GH_CLIENT_ID:
        raise HTTPException(
            status_code=500, detail="Environment secrets are missing (GH_CLIENT_ID)."
        )
    headers = {"Accept": "application/json"}
    data = {"client_id": GH_CLIENT_ID, "scope": DEVICE_FLOW_SCOPE}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=GH_DEVICE_CODE_URL, data=data, headers=headers
        )
    if response.status_code != 200:
        log.error("Device code request failed: %s", response.text)
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text or "Failed to get device code",
        )
    result = response.json()
    if "error" in result:
        log.error("Device code error: %s", result)
        raise HTTPException(
            status_code=400,
            detail=result.get("error_description", result.get("error", "Unknown error")),
        )
    return {
        "device_code": result.get("device_code"),
        "user_code": result.get("user_code"),
        "verification_uri": result.get("verification_uri"),
        "expires_in": result.get("expires_in"),
        "interval": result.get("interval", 5),
    }


@router.post("/device/token", status_code=200)
async def device_token(device_code: str):
    """
    Poll during device flow. Pass the device_code from POST /login/device/code.
    Returns access_token when the user has authorized; otherwise raises with
    authorization_pending, slow_down, expired_token, or access_denied.
    """
    if not GH_CLIENT_ID:
        raise HTTPException(
            status_code=500, detail="Environment secrets are missing (GH_CLIENT_ID)."
        )
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GH_CLIENT_ID,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url=GH_TOKEN_URL, data=data, headers=headers)
    result = response.json()

    if "error" in result:
        error = result.get("error")
        desc = result.get("error_description", error)
        if error == "authorization_pending":
            raise HTTPException(status_code=202, detail=desc)
        if error == "slow_down":
            raise HTTPException(status_code=429, detail=desc)
        if error in ("expired_token", "token_expired"):
            raise HTTPException(status_code=410, detail=desc)
        if error == "access_denied":
            raise HTTPException(status_code=403, detail=desc)
        if error == "incorrect_device_code":
            raise HTTPException(status_code=400, detail=desc)
        raise HTTPException(status_code=400, detail=desc)

    token = result.get("access_token")
    if not token:
        raise HTTPException(status_code=500, detail="No access_token in response")

    # Validate user is in Ceph org (same as web callback)
    headers = {"Authorization": "token " + token, "Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        response_org = await client.get(
            url=GH_FETCH_MEMBERSHIP_URL, headers=headers
        )
    if response_org.status_code == 404:
        log.error("User is not part of the Ceph Organization")
        raise HTTPException(
            status_code=403,
            detail="User is not part of the Ceph Organization, please contact admin",
        )
    if response_org.status_code != 200:
        log.error("Membership check failed: %s", response_org.text)
        raise HTTPException(
            status_code=response_org.status_code,
            detail="Failed to verify organization membership",
        )

    return {
        "access_token": token,
        "token_type": result.get("token_type", "bearer"),
        "scope": result.get("scope"),
    }
