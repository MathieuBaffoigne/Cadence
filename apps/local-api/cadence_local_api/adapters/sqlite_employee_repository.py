from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import time
from pathlib import Path

from cadence_local_api.domain.models.employee import Employee, WeeklyAvailability
from cadence_local_api.domain.ports.employee_repository import EmployeeRepository


@dataclass
class SqliteEmployeeRepository(EmployeeRepository):
    """Adapter: implements EmployeeRepository using SQLite."""

    db_path: Path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create(self, employee: Employee) -> Employee:
        conn = self._connect()
        try:
            cursor = conn.execute(
                "INSERT INTO employees (name, role) VALUES (?, ?)",
                (employee.name, employee.role),
            )
            conn.commit()
            return Employee(id=cursor.lastrowid, name=employee.name, role=employee.role)
        finally:
            conn.close()

    def get(self, employee_id: int) -> Employee | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT id, name, role FROM employees WHERE id = ?", (employee_id,)
            ).fetchone()
            if row is None:
                return None
            return Employee(
                id=row[0],
                name=row[1],
                role=row[2],
                availabilities=self._list_availabilities(conn, row[0]),
            )
        finally:
            conn.close()

    def list(self) -> list[Employee]:
        conn = self._connect()
        try:
            rows = conn.execute("SELECT id, name, role FROM employees").fetchall()
            return [
                Employee(
                    id=row[0],
                    name=row[1],
                    role=row[2],
                    availabilities=self._list_availabilities(conn, row[0]),
                )
                for row in rows
            ]
        finally:
            conn.close()

    def update(self, employee: Employee) -> Employee:
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE employees SET name = ?, role = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ?",
                (employee.name, employee.role, employee.id),
            )
            conn.commit()
            return employee
        finally:
            conn.close()

    def delete(self, employee_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            conn.commit()
        finally:
            conn.close()

    def add_availability(
        self, employee_id: int, availability: WeeklyAvailability
    ) -> WeeklyAvailability:
        conn = self._connect()
        try:
            cursor = conn.execute(
                "INSERT INTO employee_availabilities "
                "(employee_id, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?)",
                (
                    employee_id,
                    availability.day_of_week,
                    availability.start_time.isoformat(),
                    availability.end_time.isoformat(),
                ),
            )
            conn.commit()
            return WeeklyAvailability(
                id=cursor.lastrowid,
                employee_id=employee_id,
                day_of_week=availability.day_of_week,
                start_time=availability.start_time,
                end_time=availability.end_time,
            )
        finally:
            conn.close()

    def remove_availability(self, availability_id: int) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "DELETE FROM employee_availabilities WHERE id = ?", (availability_id,)
            )
            conn.commit()
        finally:
            conn.close()

    def _list_availabilities(
        self, conn: sqlite3.Connection, employee_id: int
    ) -> list[WeeklyAvailability]:
        rows = conn.execute(
            "SELECT id, day_of_week, start_time, end_time FROM employee_availabilities "
            "WHERE employee_id = ? ORDER BY day_of_week, start_time",
            (employee_id,),
        ).fetchall()
        return [
            WeeklyAvailability(
                id=row[0],
                employee_id=employee_id,
                day_of_week=row[1],
                start_time=time.fromisoformat(row[2]),
                end_time=time.fromisoformat(row[3]),
            )
            for row in rows
        ]
