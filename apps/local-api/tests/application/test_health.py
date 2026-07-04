from cadence_local_api.application.health import CheckHealthUseCase, HealthStatus
from cadence_local_api.domain.ports import HealthRepository


class FakeHealthRepository(HealthRepository):
    """In-memory test double for HealthRepository — no SQLite involved."""

    def __init__(self) -> None:
        self._pings: int = 0

    def record_ping(self) -> None:
        self._pings += 1

    def count_pings(self) -> int:
        return self._pings


class TestCheckHealthUseCase:
    def test_reports_ok_status_backed_by_sqlite(self) -> None:
        use_case = CheckHealthUseCase(FakeHealthRepository())

        result = use_case.execute()

        assert result == HealthStatus(status="ok", db="sqlite", ping_count=1)

    def test_counts_a_ping_on_every_execution(self) -> None:
        repository = FakeHealthRepository()
        use_case = CheckHealthUseCase(repository)

        use_case.execute()
        use_case.execute()
        result = use_case.execute()

        assert result.ping_count == 3
