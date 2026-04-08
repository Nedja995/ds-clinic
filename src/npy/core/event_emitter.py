from npy.core.logger import setup_logger
from typing import Any, Callable
from dataclasses import dataclass

logger = setup_logger()

class EventEmitter:
    """Pure-Python, Tkinter-free observer. Holds N callables and fires them all."""
    def __init__(self) -> None:
        self._listeners: list[Callable] = []

    def subscribe(self, fn: Callable) -> None:
        self._listeners.append(fn)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for fn in self._listeners:
            fn(*args, **kwargs)
            
            
@dataclass
class ErrorMessageEvent:
    """Payload emitted by the ViewModel when an error message needs to be shown."""
    title: str
    message: str