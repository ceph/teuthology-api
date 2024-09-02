from typing import Optional

from pydantic import BaseModel

from teuthology_api.schemas.suite import SuiteArgs


class PresetArgs(BaseModel):
    name: str
    cmd: SuiteArgs

    def model_post_init(self, __context):
        self.cmd = self.cmd.model_dump(by_alias=True, exclude_unset=True)


class PresetUpdateArgs(BaseModel):
    name: Optional[str] = None
    cmd: Optional[SuiteArgs] = None

    def model_post_init(self, __context):
        if self.cmd:
            self.cmd = self.cmd.model_dump(by_alias=True, exclude_unset=True)
