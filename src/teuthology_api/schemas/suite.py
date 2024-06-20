from typing import Union
from pydantic import Field

from teuthology_api.schemas.base import BaseArgs


class SuiteArgs(BaseArgs):
    # pylint: disable=too-few-public-methods
    """
    Standard arguments
    """
    arch: Union[str, None] = Field(default=None, alias="--arch")
    ceph: Union[str, None] = Field(default="main", alias="--ceph")
    ceph_repo: Union[str, None] = Field(
        default="https://github.com/ceph/ceph-ci.git", alias="--ceph-repo"
    )
    distro: Union[str, None] = Field(default=None, alias="--distro")
    distro_version: Union[str, None] = Field(default=None, alias="--distro-version")
    email: Union[str, None] = Field(default=None, alias="--email")
    flavor: Union[str, None] = Field(default="default", alias="--flavor")
    kernel: Union[str, None] = Field(default="distro", alias="--kernel")
    machine_type: Union[str, None] = Field(default="smithi", alias="--machine-type")
    newest: Union[str, None] = Field(default="0", alias="--newest")
    rerun_status: Union[bool, None] = Field(default=False, alias="--rerun-status.")
    rerun_statuses: Union[str, None] = Field(
        default="fail,dead", alias="--rerun-statuses"
    )
    sha1: Union[str, None] = Field(default=None, alias="--sha1")
    sleep_before_teardown: Union[str, None] = Field(
        default="0", alias="--sleep-before-teardown"
    )
    suite: str = Field(alias="--suite")
    suite_branch: Union[str, None] = Field(default=None, alias="--suite-branch")
    suite_dir: Union[str, None] = Field(default=None, alias="--suite-dir")
    suite_relpath: Union[str, None] = Field(default="qa", alias="--suite-relpath")
    suite_repo: Union[str, None] = Field(
        default="https://github.com/ceph/ceph-ci.git", alias="--suite_repo"
    )
    teuthology_branch: Union[str, None] = Field(
        default=None, alias="--teuthology-branch"
    )
    validate_sha1: Union[str, None] = Field(default="true", alias="--validate-sha1")
    wait: Union[bool, None] = Field(default=False, alias="--wait")
    config_yaml: Union[list, None] = Field(default=[], alias="<config_yaml>")
    """
    Scheduler arguments
    """
    owner: Union[str, None] = Field(default=None, alias="--owner")
    num: Union[str, None] = Field(default="1", alias="--num")
    priority: Union[str, None] = Field(default="70", alias="--priority")
    queue_backend: Union[str, None] = Field(default=None, alias="--queue-backend")
    rerun: Union[str, None] = Field(default=None, alias="--rerun")
    seed: Union[str, None] = Field(default="-1", alias="--seed")
    force_priority: Union[bool, None] = Field(default=False, alias="--force-priority")
    no_nested_subset: Union[bool, None] = Field(
        default=False, alias="--no-nested-subset"
    )
    job_threshold: Union[str, None] = Field(default="500", alias="--job-threshold")
    archive_upload: Union[str, None] = Field(default=None, alias="--archive-upload")
    archive_upload_url: Union[str, None] = Field(
        default=None, alias="--archive-upload-url"
    )
    throttle: Union[str, None] = Field(default=None, alias="--throttle")
    filter: Union[str, None] = Field(default=None, alias="--filter")
    filter_out: Union[str, None] = Field(default=None, alias="--filter-out")
    filter_all: Union[str, None] = Field(default=None, alias="--filter-all")
    filter_fragments: Union[str, None] = Field(
        default="false", alias="--filter-fragments"
    )
    subset: Union[str, None] = Field(default=None, alias="--subset")
    timeout: Union[str, None] = Field(default="43200", alias="--timeout")
    rocketchat: Union[str, None] = Field(default=None, alias="--rocketchat")
    limit: Union[str, None] = Field(default="0", alias="--limit")
