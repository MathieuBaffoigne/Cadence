from dataclasses import dataclass, field
from datetime import time


@dataclass
class WeeklyAvailability:
    day_of_week: int
    start_time: time
    end_time: time
    id: int | None = None
    employee_id: int | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.day_of_week <= 6:
            raise ValueError(f"day_of_week must be between 0 and 6, got {self.day_of_week}")
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")


@dataclass
class Employee:
    name: str
    role: str | None = None
    id: int | None = None
    availabilities: list[WeeklyAvailability] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")
