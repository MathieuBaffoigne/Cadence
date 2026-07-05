from dataclasses import dataclass

from cadence_local_api.domain.ports.health_repository import HealthRepository


@dataclass(frozen=True)
class HealthStatus:
    status: str
    db: str
    ping_count: int


@dataclass
class CheckHealthUseCase:
    """Application layer: orchestrates the health check, independent of FastAPI or SQLite."""

    health_repository: HealthRepository

    def execute(self) -> HealthStatus:
        self.health_repository.record_ping()
        return HealthStatus(
            status="ok",
            db="sqlite",
            ping_count=self.health_repository.count_pings(),
        )
