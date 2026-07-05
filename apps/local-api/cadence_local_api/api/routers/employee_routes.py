from dataclasses import dataclass
from datetime import time

from fastapi import APIRouter, Depends, HTTPException

from cadence_local_api.api.dependencies.employee_deps import (
    get_add_availability_use_case,
    get_create_employee_use_case,
    get_delete_employee_use_case,
    get_get_employee_use_case,
    get_list_employees_use_case,
    get_remove_availability_use_case,
    get_update_employee_use_case,
)
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

router = APIRouter()


@dataclass
class EmployeeRequest:
    name: str
    role: str | None = None


@dataclass
class AvailabilityRequest:
    day_of_week: int
    start_time: time
    end_time: time


@router.post("/employees", status_code=201)
def create_employee(
    request: EmployeeRequest,
    use_case: CreateEmployeeUseCase = Depends(get_create_employee_use_case),
) -> Employee:
    return use_case.execute(name=request.name, role=request.role)


@router.get("/employees")
def list_employees(
    use_case: ListEmployeesUseCase = Depends(get_list_employees_use_case),
) -> list[Employee]:
    return use_case.execute()


@router.get("/employees/{employee_id}")
def get_employee(
    employee_id: int,
    use_case: GetEmployeeUseCase = Depends(get_get_employee_use_case),
) -> Employee:
    employee = use_case.execute(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    request: EmployeeRequest,
    use_case: UpdateEmployeeUseCase = Depends(get_update_employee_use_case),
) -> Employee:
    return use_case.execute(employee_id=employee_id, name=request.name, role=request.role)


@router.delete("/employees/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    use_case: DeleteEmployeeUseCase = Depends(get_delete_employee_use_case),
) -> None:
    use_case.execute(employee_id)


@router.post("/employees/{employee_id}/availabilities", status_code=201)
def add_availability(
    employee_id: int,
    request: AvailabilityRequest,
    use_case: AddAvailabilityUseCase = Depends(get_add_availability_use_case),
) -> WeeklyAvailability:
    return use_case.execute(
        employee_id=employee_id,
        day_of_week=request.day_of_week,
        start_time=request.start_time,
        end_time=request.end_time,
    )


@router.delete("/availabilities/{availability_id}", status_code=204)
def remove_availability(
    availability_id: int,
    use_case: RemoveAvailabilityUseCase = Depends(get_remove_availability_use_case),
) -> None:
    use_case.execute(availability_id)
