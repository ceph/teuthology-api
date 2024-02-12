from datetime import datetime
import logging
import threading
import teuthology.suite

from fastapi import HTTPException

from teuthology_api.services.helpers import logs_run, get_run_details

log = logging.getLogger(__name__)


TEUTHOLOGY_SUIT_MAIN_TIMEOUT = 60 #seconds

def timeout_wrapper(timeout: int, func, *args, **kwargs):
    result = None

    def worker():
        nonlocal result
        result = func(*args, **kwargs)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        log.error("Task timed out and was canceled")
        thread.join()  # Ensure the thread terminates completely
        result = None

    return result

def run(args, dry_run: bool, send_logs: bool, access_token: str):
    """
    Schedule a suite.
    :returns: Run details (dict) and logs (list).
    """
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="You need to be logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        args["--timestamp"] = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        if dry_run:
            args["--dry-run"] = True
            logs = logs_run(teuthology.suite.main, args)
            return {"run": {}, "logs": logs}

        logs = []
        if send_logs:
            logs = logs_run(teuthology.suite.main, args)
        else:
            result = timeout_wrapper(TEUTHOLOGY_SUIT_MAIN_TIMEOUT, teuthology.suite.main, args)
            if result is None:
                raise TimeoutError("teuthology.suite.main timed out.")

        # get run details from paddles
        run_name = make_run_name(
            {
                "machine_type": args["--machine-type"],
                "user": args["--user"],
                "timestamp": args["--timestamp"],
                "suite": args["--suite"],
                "ceph_branch": args["--ceph"],
                "kernel_branch": args["--kernel"],
                "flavor": args["--flavor"],
            }
        )
        run_details = get_run_details(run_name)
        return {"run": run_details, "logs": logs}
    except Exception as exc:
        log.error("teuthology.suite.main failed with the error: %s", repr(exc))
        raise HTTPException(status_code=500, detail=repr(exc)) from exc


def make_run_name(run_dic):
    """
    Generate a run name. A run name looks like:
    teuthology-2014-06-23_19:00:37-rados-dumpling-testing-basic-plan
    """
    if "," in run_dic["machine_type"]:
        worker = "multi"
    else:
        worker = run_dic["machine_type"]

    return "-".join(
        [
            run_dic["user"],
            str(run_dic["timestamp"]),
            run_dic["suite"],
            run_dic["ceph_branch"],
            run_dic["kernel_branch"] or "distro",
            run_dic["flavor"],
            worker,
        ]
    ).replace("/", ":")
