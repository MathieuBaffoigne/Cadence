from abc import ABC, abstractmethod


class HealthRepository(ABC):
    """Port: persists and counts health-check pings."""

    @abstractmethod
    def record_ping(self) -> None: ...

    @abstractmethod
    def count_pings(self) -> int: ...
