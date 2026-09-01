from __future__ import annotations

from collections import UserList
from enum import Enum
from typing import Any, Callable, Generic, Iterator, TypeVar

from pydantic import BaseModel, Field

from models.patient import MedicalReport


class TaskStatus(str, Enum):
    RUNNING = "running"
    PROGRESS = "progress"
    FINISHED = "finished"
    CANCELED = "canceled"
    FAILED = "failed"


class ProgressEvent(BaseModel):
    status: TaskStatus
    elapsed_seconds: int = Field(default=0, ge=0)
    message: str = ""
    result: MedicalReport | str | None = None


T = TypeVar("T")


class ObservableList(UserList[T], Generic[T]):
    """An observable list that notifies subscribers on mutation."""

    def __init__(self, initlist: list[T] | None = None) -> None:
        super().__init__(initlist)
        self._callbacks: list[Callable[[list[T]], None]] = []

    def bind(self, callback: Callable[[list[T]], None]) -> None:
        self._callbacks.append(callback)

    def _notify(self) -> None:
        for callback in self._callbacks:
            callback(self.data)

    def append(self, item: T) -> None:
        super().append(item)
        self._notify()

    def remove(self, item: T) -> None:
        super().remove(item)
        self._notify()

    def extend(self, other: Any) -> None:
        super().extend(other)
        self._notify()

    def clear(self) -> None:
        super().clear()
        self._notify()

    def __setitem__(self, i: Any, item: Any) -> None:
        super().__setitem__(i, item)
        self._notify()

    def __delitem__(self, i: Any) -> None:
        super().__delitem__(i)
        self._notify()

    def __iter__(self) -> Iterator[T]:
        return super().__iter__()
