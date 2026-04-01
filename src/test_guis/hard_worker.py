"""
api_hardwork.worker
-------------------
Simulates a blocking long-running task.

Caller runs `run_hardwork()` in a background thread.
Progress events are pushed into a `queue.Queue[ProgressEvent]`
so the main (GUI) thread can consume them safely.

Event lifecycle:
    RUNNING  -> emitted once on task start
    PROGRESS -> emitted every second with elapsed_seconds
    FINISHED -> emitted on successful completion, carries result text
    CANCELED -> emitted when cancel_event is set by the caller
    FAILED   -> emitted on unexpected exception
"""

import queue
import threading
import time
from enum import Enum
from models import ProgressEvent, TaskStatus

# ── Constants ────────────────────────────────────────────────────────────────

TASK_DURATION_SECONDS: int = 10
RESULT_TEXT: str = "Hello i am done"




# ── Worker entry-point ────────────────────────────────────────────────────────

def run_hardwork(
    result_queue: queue.Queue,
    cancel_event: threading.Event,
) -> None:
    """
    Blocking function — always run in a daemon thread.

    Args:
        result_queue:  Thread-safe queue; caller polls this for ProgressEvents.
        cancel_event:  Set this from the main thread to request cancellation.
    """
    try:
        result_queue.put(ProgressEvent(
            status=TaskStatus.RUNNING,
            message="Task started",
        ))

        for elapsed_second in range(1, TASK_DURATION_SECONDS + 1):
            time.sleep(1)

            if cancel_event.is_set():
                result_queue.put(ProgressEvent(
                    status=TaskStatus.CANCELED,
                    elapsed_seconds=elapsed_second,
                    message=f"Task canceled after {elapsed_second}s",
                ))
                return

            result_queue.put(ProgressEvent(
                status=TaskStatus.PROGRESS,
                elapsed_seconds=elapsed_second,
                message=f"Working… {elapsed_second}/{TASK_DURATION_SECONDS} s",
            ))

        result_queue.put(ProgressEvent(
            status=TaskStatus.FINISHED,
            elapsed_seconds=TASK_DURATION_SECONDS,
            message="Task completed successfully",
            result=RESULT_TEXT,
        ))

    except Exception as exc:  # noqa: BLE001
        result_queue.put(ProgressEvent(
            status=TaskStatus.FAILED,
            message=f"Unexpected error: {exc}",
        ))