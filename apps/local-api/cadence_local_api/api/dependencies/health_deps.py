from functools import lru_cache

from cadence_local_api.application.health import CheckHealthUseCase
from cadence_local_api.adapters.sqlite_health_repository import (
    SqliteHealthRepository,
)
from cadence_local_api.settings import DB_PATH


@lru_cache
def get_health_use_case() -> CheckHealthUseCase:
    repository = SqliteHealthRepository(DB_PATH)
    return CheckHealthUseCase(repository)
