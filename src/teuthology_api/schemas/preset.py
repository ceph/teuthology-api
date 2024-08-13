from pydantic import BaseModel

from teuthology_api.schemas.suite import SuiteArgs


class PresetArgs(BaseModel):
    name: str
    suite: str
    cmd: SuiteArgs

    def model_post_init(self, __context):
        self.cmd = self.cmd.model_dump()
