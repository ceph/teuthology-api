from pydantic import BaseModel, Field
from typing import Union


class PresetsSchema(BaseModel):
    # pylint: disable=too-few-public-methods
    """
    Class for Presets Schema.
    """
    username: Union[str, None] = Field(default=None)
    name: Union[str, None] = Field(default=None)
    suite: Union[str, None] = Field(default=None)
    cmd: Union[str, None] = Field(default=None)
