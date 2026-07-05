import sqlite3
from dataclasses import dataclass
from pathlib import Path

from cadence_local_api.domain.ports.health_repository import HealthRepository


@dataclass
class SqliteHealthRepository(HealthRepository):
    """Adapter: implements the HealthRepository port using SQLite."""

    db_path: Path

    def __post_init__(self) -> None:
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS ping ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "checked_at TEXT DEFAULT CURRENT_TIMESTAMP)"
            )
            conn.commit()
        finally:
            conn.close()

    def record_ping(self) -> None:
        conn = self._connect()
        try:
            conn.execute("INSERT INTO ping DEFAULT VALUES")
            conn.commit()
        finally:
            conn.close()

    def count_pings(self) -> int:
        conn = self._connect()
        try:
            row = conn.execute("SELECT COUNT(*) FROM ping").fetchone()
            return int(row[0])
        finally:
            conn.close()
