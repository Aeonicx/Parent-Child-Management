import sched
import time
import threading
from typing import Callable, Optional, Tuple

# Create a scheduler instance
scheduler = sched.scheduler(time.time, time.sleep)


def start_scheduler():
    """
    Start the scheduler in a separate thread.
    """
    # Ensure the scheduler runs in a separate thread
    threading.Thread(target=scheduler.run).start()


def schedule_job(delay_seconds: int, func: Callable, args: Optional[Tuple] = None):
    """
    Schedule a function to be executed after a certain delay.

    :param delay_seconds: Delay in seconds before the function is executed
    :param func: The function to be executed
    :param args: Optional tuple of arguments to pass to the function
    """
    if args is None:
        args = ()
    scheduler.enter(delay_seconds, 1, func, args)
    start_scheduler()
