import sqlite3
from pathlib import Path

from tests.conftest import run_migrations

EXPECTED_TABLES: dict[str, set[str]] = {
    "clients": {"id", "name", "email", "phone", "created_at", "updated_at"},
    "employees": {"id", "name", "role", "created_at", "updated_at"},
    "employee_availabilities": {
        "id",
        "employee_id",
        "day_of_week",
        "start_time",
        "end_time",
        "created_at",
        "updated_at",
    },
    "plannings": {
        "id",
        "employee_id",
        "start_at",
        "end_at",
        "created_at",
        "updated_at",
    },
    "devis": {
        "id",
        "client_id",
        "status",
        "amount_cents",
        "created_at",
        "updated_at",
    },
    "factures": {
        "id",
        "devis_id",
        "client_id",
        "status",
        "amount_cents",
        "issued_at",
        "created_at",
        "updated_at",
    },
}


def _columns(db_path: Path, table: str) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return {row[1] for row in rows}
    finally:
        conn.close()


class TestSchemaMigrations:
    def test_creates_every_expected_table_with_its_columns(
        self, tmp_path: Path
    ) -> None:
        db_path = tmp_path / "test.db"

        run_migrations(db_path)

        for table, expected_columns in EXPECTED_TABLES.items():
            assert expected_columns <= _columns(db_path, table)

    def test_every_table_has_an_updated_at_column_for_future_sync(
        self, tmp_path: Path
    ) -> None:
        db_path = tmp_path / "test.db"

        run_migrations(db_path)

        for table in EXPECTED_TABLES:
            assert "updated_at" in _columns(db_path, table)
