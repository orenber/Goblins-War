import time
from threading import Timer
from typing import Callable, Any, Tuple, Dict, Optional
from Utility import is_member  # Assuming this is a custom utility


class TicTocGenerator:
    """Generator that yields time differences between consecutive calls"""

    def __init__(self):
        self._ti = time.time()

    def __iter__(self):
        return self

    def __next__(self):
        tf = time.time()
        time_diff = tf - self._ti
        self._ti = tf
        return time_diff


class TimerController:
    """
    A more robust repeating timer with better error handling and state management.
    """

    def __init__(self, interval: float = 1.0,
                 start_func: Optional[Callable] = None,
                 *args, **kwargs):
        """
        Initialize the repeating timer.
        """
        self._timer = None
        self.interval = max(0.001, float(interval))
        self.timer_function = start_func
        self._stop_function = None
        self._is_running = False
        self.time_limit = 10.0

        # Argument storage
        self._start_args = args
        self._start_kwargs = kwargs
        self._stop_args = ()
        self._stop_kwargs = {}

        # Timing control
        self._start_time = 0.0
        self._time_accumulator = 0.0
        self._time_gen = TicTocGenerator()  # Create generator instance

    @property
    def is_running(self) -> bool:
        """Check if the timer is currently running"""
        return self._is_running

    @property
    def elapsed_time(self) -> float:
        """Get total elapsed time since start"""
        return self._time_accumulator

    @property
    def stop_function(self) -> Optional[Callable]:
        """Get the current stop callback function"""
        return self._stop_function

    @stop_function.setter
    def stop_function(self, func: Optional[Callable]):
        """Set the stop callback function"""
        if func is None or callable(func):
            self._stop_function = func

    def configure(self, **settings) -> None:
        """
        Configure multiple timer properties at once.

        Valid settings:
        - interval: float
        - timer_function: callable
        - start_args: tuple
        - start_kwargs: dict
        - stop_function: callable
        - stop_args: tuple
        - stop_kwargs: dict
        - time_limit: float
        """
        valid_settings = {
            'interval', 'timer_function', 'start_args', 'start_kwargs',
            'stop_function', 'stop_args', 'stop_kwargs', 'time_limit'
        }

        if not is_member(list(settings.keys()), valid_settings):
            raise ValueError("Invalid setting(s) provided")

        for name, value in settings.items():
            setattr(self, name, value)

    def _execute_cycle(self) -> None:
        """Internal method that handles each timer cycle"""
        if not self._is_running:
            return

        try:
            # Execute the timer function
            if callable(self.timer_function):
                self.timer_function(*self._start_args, **self._start_kwargs)

            # Update timing
            self._time_accumulator += next(self._time_gen)

            # Check time limit
            if self._time_accumulator >= self.time_limit:
                self.stop()
                return

            # Restart the timer if still running
            if self._is_running:
                self._timer = Timer(self.interval, self._execute_cycle)
                self._timer.start()

        except Exception as e:
            self.stop()
            raise RuntimeError(f"Timer callback failed: {str(e)}") from e

    def start(self) -> None:
        """Start the repeating timer"""
        if self._is_running:
            return

        self._is_running = True
        self._time_accumulator = 0.0
        next(self._time_gen)  # Initialize timing
        self._execute_cycle()

    def stop(self) -> None:
        """Stop the timer and execute stop callback if defined"""
        if not self._is_running:
            return

        self._is_running = False
        if self._timer is not None:
            self._timer.cancel()

        if callable(self._stop_function):
            try:
                self._stop_function(*self._stop_args, **self._stop_kwargs)
            except Exception as e:
                raise RuntimeError(f"Stop callback failed: {str(e)}") from e


# Example usage
if __name__ == "__main__":
    def greeting(name: str):
        print(f"Hello {name}! (Time: {time.time():.2f})")


    def cleanup():
        print("Timer finished!")


    # Create and configure timer
    timer = TimerController(interval=0.5, start_func=greeting)
    timer.configure(
        start_args=("World",),
        stop_function=cleanup,
        time_limit=2.5
    )

    try:
        print("Starting timer...")
        timer.start()
        time.sleep(3)  # Let it run
    finally:
        timer.stop()
        print("Done.")