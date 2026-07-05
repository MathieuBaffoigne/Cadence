from pathlib import Path

from cadence_local_api.adapters.sqlite_health_repository import (
    SqliteHealthRepository,
)


class TestSqliteHealthRepository:
    def test_starts_at_zero_pings(self, tmp_path: Path) -> None:
        repository = SqliteHealthRepository(tmp_path / "test.db")

        assert repository.count_pings() == 0

    def test_counts_recorded_pings(self, tmp_path: Path) -> None:
        repository = SqliteHealthRepository(tmp_path / "test.db")

        repository.record_ping()
        repository.record_ping()

        assert repository.count_pings() == 2

    def test_persists_across_repository_instances(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        SqliteHealthRepository(db_path).record_ping()

        reopened = SqliteHealthRepository(db_path)

        assert reopened.count_pings() == 1
