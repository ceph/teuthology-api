import logging
import os
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

PULPITO_URL = os.getenv("PULPITO_URL")
log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/logout",
    tags=["logout"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=200)
def logout(request: Request):
    """
    GET route for logging out.
    """
    user = request.session.get("user")
    if user:
        request.session.pop("user", None)
        return RedirectResponse(request.url)
    log.warning("No session found, probably already logged out.")
    raise HTTPException(
        status_code=204, detail="No session found, probably already logged out."
    )
