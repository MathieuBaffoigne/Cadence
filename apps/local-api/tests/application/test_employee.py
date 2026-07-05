from datetime import time

from cadence_local_api.application.employee import (
    AddAvailabilityUseCase,
    CreateEmployeeUseCase,
    DeleteEmployeeUseCase,
    GetEmployeeUseCase,
    ListEmployeesUseCase,
    RemoveAvailabilityUseCase,
    UpdateEmployeeUseCase,
)
from cadence_local_api.domain.models.employee import Employee, WeeklyAvailability
from cadence_local_api.domain.ports.employee_repository import EmployeeRepository


class FakeEmployeeRepository(EmployeeRepository):
    """In-memory test double for EmployeeRepository — no SQLite involved."""

    def __init__(self) -> None:
        self._employees: dict[int, Employee] = {}
        self._availabilities: dict[int, WeeklyAvailability] = {}
        self._next_employee_id = 1
        self._next_availability_id = 1

    def create(self, employee: Employee) -> Employee:
        created = Employee(
            id=self._next_employee_id, name=employee.name, role=employee.role
        )
        self._employees[created.id] = created
        self._next_employee_id += 1
        return created

    def get(self, employee_id: int) -> Employee | None:
        employee = self._employees.get(employee_id)
        if employee is None:
            return None
        availabilities = [
            availability
            for availability in self._availabilities.values()
            if availability.employee_id == employee_id
        ]
        return Employee(
            id=employee.id,
            name=employee.name,
            role=employee.role,
            availabilities=availabilities,
        )

    def list(self) -> list[Employee]:
        return [self.get(employee_id) for employee_id in self._employees]

    def update(self, employee: Employee) -> Employee:
        self._employees[employee.id] = employee
        return employee

    def delete(self, employee_id: int) -> None:
        self._employees.pop(employee_id, None)

    def add_availability(
        self, employee_id: int, availability: WeeklyAvailability
    ) -> WeeklyAvailability:
        created = WeeklyAvailability(
            id=self._next_availability_id,
            employee_id=employee_id,
            day_of_week=availability.day_of_week,
            start_time=availability.start_time,
            end_time=availability.end_time,
        )
        self._availabilities[created.id] = created
        self._next_availability_id += 1
        return created

    def remove_availability(self, availability_id: int) -> None:
        self._availabilities.pop(availability_id, None)


class TestCreateEmployeeUseCase:
    def test_creates_an_employee_with_a_name_and_role(self) -> None:
        use_case = CreateEmployeeUseCase(FakeEmployeeRepository())

        employee = use_case.execute(name="Alice", role="fleuriste")

        assert employee.id is not None
        assert employee.name == "Alice"
        assert employee.role == "fleuriste"


class TestListEmployeesUseCase:
    def test_lists_every_created_employee(self) -> None:
        repository = FakeEmployeeRepository()
        CreateEmployeeUseCase(repository).execute(name="Alice")
        CreateEmployeeUseCase(repository).execute(name="Bob")

        employees = ListEmployeesUseCase(repository).execute()

        assert {employee.name for employee in employees} == {"Alice", "Bob"}


class TestGetEmployeeUseCase:
    def test_returns_none_for_an_unknown_employee(self) -> None:
        use_case = GetEmployeeUseCase(FakeEmployeeRepository())

        assert use_case.execute(999) is None


class TestUpdateEmployeeUseCase:
    def test_updates_the_employees_name_and_role(self) -> None:
        repository = FakeEmployeeRepository()
        created = CreateEmployeeUseCase(repository).execute(name="Alice", role="fleuriste")

        updated = UpdateEmployeeUseCase(repository).execute(
            employee_id=created.id, name="Alice", role="responsable"
        )

        assert updated.role == "responsable"


class TestDeleteEmployeeUseCase:
    def test_removes_the_employee(self) -> None:
        repository = FakeEmployeeRepository()
        created = CreateEmployeeUseCase(repository).execute(name="Alice")

        DeleteEmployeeUseCase(repository).execute(created.id)

        assert GetEmployeeUseCase(repository).execute(created.id) is None


class TestAddAvailabilityUseCase:
    def test_attaches_a_weekly_slot_to_the_employee(self) -> None:
        repository = FakeEmployeeRepository()
        employee = CreateEmployeeUseCase(repository).execute(name="Alice")

        AddAvailabilityUseCase(repository).execute(
            employee_id=employee.id,
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )

        fetched = GetEmployeeUseCase(repository).execute(employee.id)
        assert len(fetched.availabilities) == 1
        assert fetched.availabilities[0].day_of_week == 1


class TestRemoveAvailabilityUseCase:
    def test_detaches_the_slot_from_the_employee(self) -> None:
        repository = FakeEmployeeRepository()
        employee = CreateEmployeeUseCase(repository).execute(name="Alice")
        availability = AddAvailabilityUseCase(repository).execute(
            employee_id=employee.id,
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )

        RemoveAvailabilityUseCase(repository).execute(availability.id)

        fetched = GetEmployeeUseCase(repository).execute(employee.id)
        assert fetched.availabilities == []
