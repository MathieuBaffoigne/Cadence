from functools import lru_cache

from fastapi import Depends

from cadence_local_api.application.employee import (
    AddAvailabilityUseCase,
    CreateEmployeeUseCase,
    DeleteEmployeeUseCase,
    GetEmployeeUseCase,
    ListEmployeesUseCase,
    RemoveAvailabilityUseCase,
    UpdateEmployeeUseCase,
)
from cadence_local_api.adapters.sqlite_employee_repository import (
    SqliteEmployeeRepository,
)
from cadence_local_api.settings import DB_PATH


@lru_cache
def get_employee_repository() -> SqliteEmployeeRepository:
    return SqliteEmployeeRepository(DB_PATH)


def get_create_employee_use_case(
    repository: SqliteEmployeeRepository = Depends(get_employee_repository),
) -> CreateEmployeeUseCase:
    return CreateEmployeeUseCase(repository)


def get_list_employees_use_case(
    repository: SqliteEmployeeRepository = Depends(get_employee_repository),
) -> ListEmployeesUseCase:
    return ListEmployeesUseCase(repository)


def get_get_employee_use_case(
    repository: SqliteEmployeeRepository = Depends(get_employee_repository),
) -> GetEmployeeUseCase:
    return GetEmployeeUseCase(repository)


def get_update_employee_use_case(
    repository: SqliteEmployeeRepository = Depends(get_employee_repository),
) -> UpdateEmployeeUseCase:
    return UpdateEmployeeUseCase(repository)


def get_delete_employee_use_case(
    repository: SqliteEmployeeRepository = Depends(get_employee_repository),
) -> DeleteEmployeeUseCase:
    return DeleteEmployeeUseCase(repository)


def get_add_availability_use_case(
    repository: SqliteEmployeeRepository = Depends(get_employee_repository),
) -> AddAvailabilityUseCase:
    return AddAvailabilityUseCase(repository)


def get_remove_availability_use_case(
    repository: SqliteEmployeeRepository = Depends(get_employee_repository),
) -> RemoveAvailabilityUseCase:
    return RemoveAvailabilityUseCase(repository)
