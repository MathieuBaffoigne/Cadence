from datetime import time

import pytest

from cadence_local_api.domain.models.employee import Employee, WeeklyAvailability


class TestEmployee:
    def test_rejects_an_empty_name(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Employee(name="  ")


class TestWeeklyAvailability:
    def test_rejects_a_day_of_week_outside_zero_to_six(self) -> None:
        with pytest.raises(ValueError, match="day_of_week"):
            WeeklyAvailability(day_of_week=7, start_time=time(9, 0), end_time=time(12, 0))

    def test_rejects_a_start_time_after_the_end_time(self) -> None:
        with pytest.raises(ValueError, match="start_time"):
            WeeklyAvailability(day_of_week=0, start_time=time(12, 0), end_time=time(9, 0))
