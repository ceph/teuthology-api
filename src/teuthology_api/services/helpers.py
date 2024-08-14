from multiprocessing import Process, Queue
import logging
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, Request
from dotenv import load_dotenv

import teuthology
import requests  # Note: import requests after teuthology
from requests.exceptions import HTTPError

load_dotenv()

PADDLES_URL = os.getenv("PADDLES_URL")
ARCHIVE_DIR = os.getenv("ARCHIVE_DIR")

log = logging.getLogger(__name__)


def logs_run(func, args):
    """
    Run the command function in a seperate process (to isolate logs),
    and return logs printed during the execution of the function.
    """
    _id = str(uuid.uuid4())
    archive = Path(ARCHIVE_DIR)
    log_file = archive / f"{_id}.log"
    teuth_queue = Queue()
    teuth_process = Process(
        target=_execute_with_logs, args=(func, args, log_file, teuth_queue)
    )
    teuth_process.daemon = True  # Set the process as a daemon
    teuth_process.start()
    teuth_process.join(timeout=180)  # Set the timeout value in seconds
    if teuth_process.is_alive():
        teuth_process.terminate()  # Terminate the process if it exceeds the timeout
        teuth_process.join()
        raise TimeoutError("Process execution timed out")
    logs = ""
    with open(log_file, encoding="utf-8") as file:
        logs = file.readlines()
    if os.path.isfile(log_file):
        os.remove(log_file)
    log.debug(logs)
    if teuth_process.exitcode > 0:
        e = teuth_queue.get()
        log.error(e)
        return "fail", e, 0
    else:
        job_count = teuth_queue.get()
        return "success", logs, job_count


def _execute_with_logs(func, args, log_file, teuth_queue):
    """
    To store logs, set a new FileHandler for teuthology root logger
    and then execute the command function.
    """
    teuthology.setup_log_file(log_file)
    try:
        job_count = func(args)
        teuth_queue.put(job_count)
    except Exception as e:
        teuth_queue.put(e)
        raise


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
            status_code=http_err.response.status_code, detail=repr(http_err)
        ) from http_err
    except Exception as err:
        log.error(err)
        raise HTTPException(status_code=500, detail=repr(err)) from err


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
