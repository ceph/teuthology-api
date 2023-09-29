from sqlalchemy.orm import Session
from models.auto_suite import AutoSuite
from schemas.auto_suite import BuildStatusWebhook
from services.suite import run


def auto_schedule(autosuite_records):
    for auto_suite in autosuite_records:
        run(auto_suite.cmd, dry_run=False, send_logs=True)


class AutoSuiteDatabaseException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


class AutoSuiteService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str):
        db_autosuite = (
            self.db.query(AutoSuite).filter(AutoSuite.username == username).all()
        )
        return db_autosuite

    def get_by_build_data(self, build_data: BuildStatusWebhook):
        distro = build_data.distro
        distro_version = build_data.distro_version
        flavor = build_data.flavor
        branch = build_data.ref
        db_preset = (
            self.db.query(AutoSuite)
            .filter(
                AutoSuite.distro == distro,
                AutoSuite.distro_version == distro_version,
                AutoSuite.flavor == flavor,
                AutoSuite.branch == branch,
            )
            .first()
        )
        return db_preset

    def create(self, new_obj: dict):
        new_autosuite = AutoSuite(**new_obj)
        self.db.add(new_autosuite)
        self.db.commit()
        self.db.refresh(new_autosuite)
        return new_autosuite

    def update(self, id: int, update_data: dict):
        autosuite_query = self.db.query(AutoSuite).filter(AutoSuite.id == id)
        db_autosuite = autosuite_query.first()
        if not db_autosuite:
            raise AutoSuiteDatabaseException(
                "AutoSuite object does not exist - unable to update.", 404
            )
        autosuite_query.filter(AutoSuite.id == id).update(
            update_data, synchronize_session=False
        )
        self.db.commit()
        self.db.refresh(db_autosuite)
        return db_autosuite
