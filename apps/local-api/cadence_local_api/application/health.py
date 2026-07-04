from dataclasses import dataclass

from cadence_local_api.domain.ports import HealthRepository


@dataclass(frozen=True)
class HealthStatus:
    status: str
    db: str
    ping_count: int


class CheckHealthUseCase:
    """Application layer: orchestrates the health check, independent of FastAPI or SQLite."""

    def __init__(self, health_repository: HealthRepository) -> None:
        self._health_repository = health_repository

    def execute(self) -> HealthStatus:
        self._health_repository.record_ping()
        return HealthStatus(
            status="ok",
            db="sqlite",
            ping_count=self._health_repository.count_pings(),
        )
