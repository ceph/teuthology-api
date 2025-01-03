from multiprocessing import Process
import logging
import os
import uuid
import httpx
from pathlib import Path

from fastapi import HTTPException, Request
from dotenv import load_dotenv

import teuthology
import requests  # Note: import requests after teuthology
from requests.exceptions import HTTPError

load_dotenv()

PADDLES_URL = os.getenv("PADDLES_URL")
ARCHIVE_DIR = os.getenv("ARCHIVE_DIR")
TEUTHOLOGY_PATH = os.getenv("TEUTHOLOGY_PATH")

ADMIN_TEAM = os.getenv("ADMIN_TEAM")
GH_ORG_TEAM_URL = os.getenv("GH_ORG_TEAM_URL")

log = logging.getLogger(__name__)


def logs_run(func, args):
    """
    Run the command function in a seperate process (to isolate logs),
    and return logs printed during the execution of the function.
    """
    _id = str(uuid.uuid4())
    archive = Path(ARCHIVE_DIR)
    log_file = archive / f"{_id}.log"

    teuthology_process = Process(target=_execute_with_logs, args=(func, args, log_file))
    teuthology_process.start()
    teuthology_process.join()

    logs = ""
    with open(log_file, encoding="utf-8") as file:
        logs = file.readlines()
    if os.path.isfile(log_file):
        os.remove(log_file)
    return logs


def _execute_with_logs(func, args, log_file):
    """
    To store logs, set a new FileHandler for teuthology root logger
    and then execute the command function.
    """
    teuthology.setup_log_file(log_file)
    func(args)


def get_run_details(run_name: str):
    """
    Queries paddles to look if run is created.
    """
    url = f"{PADDLES_URL}/runs/{run_name}/"
    try:
        run_info = requests.get(url)
        run_info.raise_for_status()
        return run_info.json()
    except HTTPError as http_err:
        log.error(http_err)
        raise HTTPException(
            status_code=http_err.response.status_code, detail=str(http_err)
        ) from http_err
    except Exception as err:
        log.error(err)
        raise HTTPException(status_code=500, detail=str(err)) from err


def get_username(request: Request):
    """
    Get username from request.session
    """
    username = request.session.get("user", {}).get("username")
    if username:
        return username
    log.error("username empty, user probably is not logged in.")
    raise HTTPException(
        status_code=401,
        detail="You need to be logged in",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_token(request: Request):
    """
    Get access token from request.session
    """
    token = request.session.get("user", {}).get("access_token")
    if token:
        return {"access_token": token, "token_type": "bearer"}
    log.error("access_token empty, user probably is not logged in.")
    raise HTTPException(
        status_code=401,
        detail="You need to be logged in",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def isAdmin(username, token):
    if not (GH_ORG_TEAM_URL and ADMIN_TEAM):
        log.error("GH_ORG_TEAM_URL or ADMIN_TEAM is not set in .env")
        return False
    if not (token and username):
        raise HTTPException(
            status_code=401,
            detail="You are probably not logged in (username or token missing)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    TEAM_MEMBER_URL = f"{GH_ORG_TEAM_URL}/{ADMIN_TEAM}/memberships/{username}"
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": "token " + token,
            "Accept": "application/json",
        }
        response_org = await client.get(url=TEAM_MEMBER_URL, headers=headers)
        if response_org:
            response_org_dict = dict(response_org.json())
            if response_org_dict.get("state", "") == "active":
                return True
        return False
