from typing import Union
from pydantic import BaseModel, Field


class BaseArgs(BaseModel):
    # pylint: disable=too-few-public-methods
    """
    Class for Base Args.
    """
    dry_run: Union[bool, None] = Field(default=False, alias="--dry-run")
    non_interactive: Union[bool, None] = Field(default=False, alias="--non-interactive")
    verbose: Union[int, None] = Field(default=1, alias="--verbose")
    help: Union[bool, None] = Field(default=False, alias="--help")
