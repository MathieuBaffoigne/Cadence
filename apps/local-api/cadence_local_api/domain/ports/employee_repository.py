from abc import ABC, abstractmethod

from cadence_local_api.domain.models.employee import Employee, WeeklyAvailability


class EmployeeRepository(ABC):
    """Port: persists employees and their weekly availabilities."""

    @abstractmethod
    def create(self, employee: Employee) -> Employee: ...

    @abstractmethod
    def get(self, employee_id: int) -> Employee | None: ...

    @abstractmethod
    def list(self) -> list[Employee]: ...

    @abstractmethod
    def update(self, employee: Employee) -> Employee: ...

    @abstractmethod
    def delete(self, employee_id: int) -> None: ...

    @abstractmethod
    def add_availability(
        self, employee_id: int, availability: WeeklyAvailability
    ) -> WeeklyAvailability: ...

    @abstractmethod
    def remove_availability(self, availability_id: int) -> None: ...
