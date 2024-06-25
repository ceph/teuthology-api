import logging
import os
import subprocess

from fastapi import HTTPException, Request

from teuthology_api.services.helpers import get_username, get_run_details


TEUTHOLOGY_PATH = os.getenv("TEUTHOLOGY_PATH")
log = logging.getLogger(__name__)


def run(args, send_logs: bool, access_token: str, request: Request):
    """
    Kill running teuthology jobs.
    """
    if not access_token:
        log.error("access_token empty, user probably is not logged in.")
        raise HTTPException(
            status_code=401,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = get_username(request)
    run_name = args.get("--run")
    if run_name:
        run_details = get_run_details(run_name)
        run_owner = run_details.get("user")
    else:
        log.error("teuthology-kill is missing --run")
        raise HTTPException(status_code=400, detail="--run is a required argument")
    # TODO if user has admin priviledge, then they can kill any run/job.
    if run_owner.lower() != username.lower():
        log.error(
            "%s doesn't have permission to kill a job scheduled by: %s",
            username,
            run_owner,
        )
        raise HTTPException(
            status_code=401, detail="You don't have permission to kill this run/job"
        )
    try:
        kill_cmd = [f"{TEUTHOLOGY_PATH}/virtualenv/bin/teuthology-kill"]
        for flag, flag_value in args.items():
            if isinstance(flag_value, bool):
                flag_value = int(flag_value)
            kill_cmd += [flag, str(flag_value)]
        log.info(kill_cmd)
        proc = subprocess.Popen(
            kill_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = proc.communicate()
        returncode = proc.wait(timeout=120)
        log.info(stdout)
        if returncode != 0:
            raise Exception(stdout)
        if send_logs:
            return {"kill": "success", "logs": stdout}
        return {"kill": "success"}
    except Exception as exc:
        log.error("teuthology-kill command failed with the error: %s", repr(exc))
        raise HTTPException(status_code=500, detail=repr(exc)) from exc
