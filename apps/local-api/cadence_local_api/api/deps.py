from functools import lru_cache
from pathlib import Path

from cadence_local_api.application.health import CheckHealthUseCase
from cadence_local_api.infrastructure.sqlite_health_repository import (
    SqliteHealthRepository,
)

DB_PATH: Path = Path(__file__).resolve().parent.parent.parent / "cadence.local.db"


@lru_cache
def get_health_use_case() -> CheckHealthUseCase:
    repository = SqliteHealthRepository(DB_PATH)
    return CheckHealthUseCase(repository)
