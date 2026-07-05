from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"


def run_migrations(db_path: Path) -> None:
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS_DIR))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(config, "head")


@pytest.fixture
def migrated_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    run_migrations(db_path)
    return db_path
