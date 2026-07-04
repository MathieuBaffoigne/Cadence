import sqlite3
from pathlib import Path

from cadence_local_api.domain.ports import HealthRepository


class SqliteHealthRepository(HealthRepository):
    """Adapter: implements the HealthRepository port using SQLite."""

    def __init__(self, db_path: Path) -> None:
        self._db_path: Path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

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
