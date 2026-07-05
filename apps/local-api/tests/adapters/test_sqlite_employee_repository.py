from datetime import time
from pathlib import Path

from cadence_local_api.domain.models.employee import Employee, WeeklyAvailability
from cadence_local_api.adapters.sqlite_employee_repository import (
    SqliteEmployeeRepository,
)


class TestSqliteEmployeeRepository:
    def test_creates_and_retrieves_an_employee(self, migrated_db: Path) -> None:
        repository = SqliteEmployeeRepository(migrated_db)

        created = repository.create(Employee(name="Alice", role="fleuriste"))
        fetched = repository.get(created.id)

        assert fetched is not None
        assert fetched.name == "Alice"
        assert fetched.role == "fleuriste"

    def test_returns_none_for_an_unknown_employee(self, migrated_db: Path) -> None:
        repository = SqliteEmployeeRepository(migrated_db)

        assert repository.get(999) is None

    def test_lists_all_employees(self, migrated_db: Path) -> None:
        repository = SqliteEmployeeRepository(migrated_db)
        repository.create(Employee(name="Alice"))
        repository.create(Employee(name="Bob"))

        employees = repository.list()

        assert {employee.name for employee in employees} == {"Alice", "Bob"}

    def test_updates_an_employee(self, migrated_db: Path) -> None:
        repository = SqliteEmployeeRepository(migrated_db)
        created = repository.create(Employee(name="Alice", role="fleuriste"))

        repository.update(Employee(id=created.id, name="Alice", role="responsable"))

        assert repository.get(created.id).role == "responsable"

    def test_deletes_an_employee(self, migrated_db: Path) -> None:
        repository = SqliteEmployeeRepository(migrated_db)
        created = repository.create(Employee(name="Alice"))

        repository.delete(created.id)

        assert repository.get(created.id) is None

    def test_adds_and_lists_availabilities_for_an_employee(
        self, migrated_db: Path
    ) -> None:
        repository = SqliteEmployeeRepository(migrated_db)
        employee = repository.create(Employee(name="Alice"))

        repository.add_availability(
            employee.id,
            WeeklyAvailability(
                day_of_week=1, start_time=time(9, 0), end_time=time(12, 0)
            ),
        )

        fetched = repository.get(employee.id)
        assert len(fetched.availabilities) == 1
        assert fetched.availabilities[0].day_of_week == 1
        assert fetched.availabilities[0].start_time == time(9, 0)

    def test_removes_an_availability(self, migrated_db: Path) -> None:
        repository = SqliteEmployeeRepository(migrated_db)
        employee = repository.create(Employee(name="Alice"))
        availability = repository.add_availability(
            employee.id,
            WeeklyAvailability(
                day_of_week=1, start_time=time(9, 0), end_time=time(12, 0)
            ),
        )

        repository.remove_availability(availability.id)

        assert repository.get(employee.id).availabilities == []

    def test_deletes_an_employee_that_still_has_availabilities(
        self, migrated_db: Path
    ) -> None:
        repository = SqliteEmployeeRepository(migrated_db)
        employee = repository.create(Employee(name="Alice"))
        repository.add_availability(
            employee.id,
            WeeklyAvailability(
                day_of_week=1, start_time=time(9, 0), end_time=time(12, 0)
            ),
        )

        repository.delete(employee.id)

        assert repository.get(employee.id) is None

    def test_persists_across_repository_instances(self, migrated_db: Path) -> None:
        SqliteEmployeeRepository(migrated_db).create(Employee(name="Alice"))

        reopened = SqliteEmployeeRepository(migrated_db)

        assert len(reopened.list()) == 1
