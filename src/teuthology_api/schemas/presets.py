from pydantic import BaseModel, Field
from typing import Union


class PresetSchema(BaseModel):
    # pylint: disable=too-few-public-methods
    """
    Class for Base Args.
    """
    username: Union[str, None] = Field(default=None)
    name: Union[str, None] = Field(default=None)
    suite: Union[str, None] = Field(default=None)
    cmd: Union[str, None] = Field(default=None)
