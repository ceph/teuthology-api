from typing import Union
from pydantic import BaseModel, Field
from .suite import SuiteArgs


class BuildStatusWebhook(BaseModel):
    # pylint: disable=too-few-public-methods
    """
    Class for Build Status Webhook.
    """
    status: str = Field(default="")
    distro: Union[str, None] = Field(default="")
    distro_version: Union[str, None] = Field(default="")
    ref: Union[str, None] = Field(default="")
    sha1: Union[str, None] = Field(default="")
    flavor: Union[str, None] = Field(default="")
    url: Union[str, None] = Field(default="")


class AutoSuiteSchema(BaseModel):
    # pylint: disable=too-few-public-methods
    """
    Class for Auto Suite Args.
    """
    username: Union[str, None] = Field(default=None)
    status: Union[str, None] = Field(default=None)
    branch: Union[str, None] = Field(default=None)
    distro: Union[str, None] = Field(default=None)
    distro_version: Union[str, None] = Field(default=None)
    flavor: Union[str, None] = Field(default=None)
    suite: Union[str, None] = Field(default=None)
    log_path: Union[str, None] = Field(default=None)
    cmd: Union[SuiteArgs, None] = Field(default=None)