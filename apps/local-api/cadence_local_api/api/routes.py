from fastapi import APIRouter, Depends

from cadence_local_api.api.deps import get_health_use_case
from cadence_local_api.application.health import CheckHealthUseCase, HealthStatus

router = APIRouter()


@router.get("/health")
def health(
    use_case: CheckHealthUseCase = Depends(get_health_use_case),
) -> HealthStatus:
    return use_case.execute()
