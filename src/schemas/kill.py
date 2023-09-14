from typing import Union
from pydantic import Field

from .base import BaseArgs


class KillArgs(BaseArgs):
    # pylint: disable=too-few-public-methods
    """
    Class for KillArgs.
    """
    owner: Union[str, None] = Field(default=None, alias="--owner")
    run: Union[str, None] = Field(default=None, alias="--run")
    preserve_queue: Union[bool, None] = Field(default=None, alias="--preserve-queue")
    job: Union[list, None] = Field(default=None, alias="--job")
    jobspec: Union[str, None] = Field(default=None, alias="--jobspec")
    machine_type: Union[str, None] = Field(default="default", alias="--machine-type")
    archive: Union[str, None] = Field(default=None, alias="--archive")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "--dry-run": False,
                    "--non-interactive": False,
                    "--verbose": 1,
                    "--help": False,
                    "--user": "<sepia_username>",
                    "--run": "<run_title>",
                    "--job": [1, 2],
                    "--machine-type": "smithi",
                }
            ]
        }
    }
