from dataclasses import dataclass
from datetime import time

from cadence_local_api.domain.models.employee import Employee, WeeklyAvailability
from cadence_local_api.domain.ports.employee_repository import EmployeeRepository


@dataclass
class CreateEmployeeUseCase:
    repository: EmployeeRepository

    def execute(self, name: str, role: str | None = None) -> Employee:
        return self.repository.create(Employee(name=name, role=role))


@dataclass
class ListEmployeesUseCase:
    repository: EmployeeRepository

    def execute(self) -> list[Employee]:
        return self.repository.list()


@dataclass
class GetEmployeeUseCase:
    repository: EmployeeRepository

    def execute(self, employee_id: int) -> Employee | None:
        return self.repository.get(employee_id)


@dataclass
class UpdateEmployeeUseCase:
    repository: EmployeeRepository

    def execute(self, employee_id: int, name: str, role: str | None = None) -> Employee:
        return self.repository.update(Employee(id=employee_id, name=name, role=role))


@dataclass
class DeleteEmployeeUseCase:
    repository: EmployeeRepository

    def execute(self, employee_id: int) -> None:
        self.repository.delete(employee_id)


@dataclass
class AddAvailabilityUseCase:
    repository: EmployeeRepository

    def execute(
        self, employee_id: int, day_of_week: int, start_time: time, end_time: time
    ) -> WeeklyAvailability:
        availability = WeeklyAvailability(
            day_of_week=day_of_week, start_time=start_time, end_time=end_time
        )
        return self.repository.add_availability(employee_id, availability)


@dataclass
class RemoveAvailabilityUseCase:
    repository: EmployeeRepository

    def execute(self, availability_id: int) -> None:
        self.repository.remove_availability(availability_id)
