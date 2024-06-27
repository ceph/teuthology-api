from datetime import datetime
from tempfile import NamedTemporaryFile
import logging
import teuthology.suite

from fastapi import HTTPException

from teuthology_api.services.helpers import logs_run, get_run_details

log = logging.getLogger(__name__)


def run(args, send_logs: bool, access_token: str):
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

        temp_files: list[NamedTemporaryFile] = []
        if "<config_yaml>" in args:
            for config in args["<config_yaml>"]:
                temp_file = NamedTemporaryFile(suffix=".yaml")
                temp_file.write(config.encode())
                temp_file.seek(0)
                temp_files.append(temp_file)
            args["<config_yaml>"] = [file.name for file in temp_files]

        logs = logs_run(teuthology.suite.main, args)

        for file in temp_files:
            file.close()

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
        if send_logs or args["--dry-run"]:
            return {"run": run_details, "logs": logs}
        return {"run": run_details}
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
