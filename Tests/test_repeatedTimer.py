import unittest
from unittest.mock import MagicMock, patch, call
import time
from threading import Timer as _ThreadingTimer

# ---------------------------------------------------------------------------
# Inline implementation so the file is self-contained.
# In your project replace this block with:
#   from Utility.timer_utility import TimerController, TicTocGenerator, tic, toc
# ---------------------------------------------------------------------------

import itertools
import threading


class TicTocGenerator:
    """
    Elapsed-time generator.
    Each call to next() returns the seconds since the *previous* call
    (or since creation for the first call).
    """
    def __init__(self):
        self._start = time.time()

    def __iter__(self):
        return self

    def __next__(self) -> float:
        now = time.time()
        elapsed = now - self._start
        self._start = now
        return elapsed


# Module-level tic/toc state
_global_timer = TicTocGenerator()

def tic() -> None:
    """Reset the global elapsed-time counter."""
    global _global_timer
    _global_timer = TicTocGenerator()

def toc() -> float:
    """Return seconds elapsed since the last tic() call."""
    return next(_global_timer)


class TimerController:
    """
    Repeating timer with configurable interval, limit, start/stop callbacks,
    and optional arguments forwarded to the timer function.
    """

    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self._timer: _ThreadingTimer = None

        # BUG FIX 1 (pre-emptive): is_running must be an instance attribute
        # managed by start()/stop(). The original tests assigned directly to
        # self.rt.is_running = True in test_stop — that only works if it is a
        # plain attribute, not a property.  Kept as plain bool.
        self.is_running: bool = False

        self.limit: float = 10          # seconds before auto-stop (0 = no limit)
        self._start_time: float = 0

        # Callable slots
        self.timer_function = None
        self.stop_function  = None

        # Argument slots
        self.start_input_args   = ()
        self.start_input_kwargs = {}
        self.stop_input_args    = ()
        self.stop_input_kwargs  = {}

        # BUG FIX 2: The fixed PhysicsObject sets start_func / stop_function
        # directly as attributes after construction (not via the constructor).
        # Expose start_func as an alias for timer_function so both APIs work.
        self.start_func = None   # alias; _run prefers start_func over timer_function

    # ------------------------------------------------------------------
    # Convenience setter
    # ------------------------------------------------------------------

    def set_attr(self, **kwargs) -> None:
        """Set any number of attributes in one call."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    # ------------------------------------------------------------------
    # Core timer logic
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Called by the threading.Timer on each tick."""
        # Time-limit check
        if self.limit and (time.time() - self._start_time) >= self.limit:
            self.stop()
            return

        # Call the user function
        fn = self.start_func if self.start_func is not None else self.timer_function
        if callable(fn):
            fn(*self.start_input_args, **self.start_input_kwargs)

        # Reschedule if still running
        if self.is_running:
            self._timer = _ThreadingTimer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()

    def start(self) -> None:
        """Start (or restart) the repeating timer."""
        if self.is_running:
            return
        self.is_running  = True
        self._start_time = time.time()
        self._timer = _ThreadingTimer(self.interval, self._run)
        self._timer.daemon = True
        self._timer.start()

    def stop(self) -> None:
        """Stop the timer and fire the stop callback."""
        if self._timer is not None:
            self._timer.cancel()
        self.is_running  = False
        self._start_time = 0

        if callable(self.stop_function):
            self.stop_function(*self.stop_input_args, **self.stop_input_kwargs)


# ===========================================================================
# Tests
# ===========================================================================

class TestTicToc(unittest.TestCase):

    def test_tic_toc_generator(self):
        """TicTocGenerator.next() returns elapsed seconds since last call."""
        gen = TicTocGenerator()
        next(gen)           # burn the first interval (since creation)
        time.sleep(0.1)
        elapsed = next(gen)
        self.assertGreater(elapsed, 0)
        self.assertAlmostEqual(elapsed, 0.1, delta=0.05)

    def test_toc(self):
        """toc() returns seconds elapsed since the last tic()."""
        tic()
        time.sleep(0.1)
        elapsed = toc()
        self.assertAlmostEqual(elapsed, 0.1, delta=0.05)


class TestTimerController(unittest.TestCase):

    def setUp(self):
        self.mock_callback = MagicMock()
        self.mock_stop     = MagicMock()
        self.rt = TimerController(interval=0.1)
        self.rt.timer_function = self.mock_callback
        self.rt.stop_function  = self.mock_stop

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def test_initialization(self):
        """TimerController initialises with expected default values."""
        rt = TimerController(interval=0.1)
        self.assertEqual(rt.interval, 0.1)
        self.assertIsNone(rt._timer)
        self.assertFalse(rt.is_running)
        self.assertEqual(rt.limit, 10)

    # ------------------------------------------------------------------
    # Property / attribute setters
    # ------------------------------------------------------------------

    def test_property_setters(self):
        """start/stop input args and kwargs round-trip correctly."""
        test_args   = (1, 2, 3)
        test_kwargs = {'a': 1, 'b': 2}

        self.rt.start_input_args   = test_args
        self.rt.start_input_kwargs = test_kwargs
        self.assertEqual(self.rt.start_input_args,   test_args)
        self.assertEqual(self.rt.start_input_kwargs, test_kwargs)

        self.rt.stop_input_args   = test_args
        self.rt.stop_input_kwargs = test_kwargs
        self.assertEqual(self.rt.stop_input_args,   test_args)
        self.assertEqual(self.rt.stop_input_kwargs, test_kwargs)

    def test_set_attr(self):
        """set_attr() applies all provided keyword arguments."""
        new_fn   = lambda: None
        stop_fn  = lambda: None
        test_attrs = {
            'interval':           0.5,
            'timer_function':     new_fn,
            'start_input_args':   (1, 2),
            'start_input_kwargs': {'x': 1},
            'stop_function':      stop_fn,
            'stop_input_args':    (3, 4),
            'stop_input_kwargs':  {'y': 2},
            'limit':              5,
        }
        self.rt.set_attr(**test_attrs)
        for attr, value in test_attrs.items():
            self.assertEqual(getattr(self.rt, attr), value)

    # ------------------------------------------------------------------
    # start
    # ------------------------------------------------------------------

    @patch('threading.Timer')
    def test_start(self, mock_timer_cls):
        """start() sets is_running and creates a threading.Timer."""
        # BUG FIX 3: Original patch target was 'threading.Timer', but our
        # inline class imports Timer as _ThreadingTimer. The patch must target
        # the name as used inside the module. Since we're inlining, patch the
        # name in this module's global scope.
        mock_instance = MagicMock()
        mock_timer_cls.return_value = mock_instance

        # Re-patch the name actually used by start() in this exec context
        import builtins
        original = _ThreadingTimer
        try:
            # Directly replace in the global dict for the duration of the call
            globals()['_ThreadingTimer'] = mock_timer_cls
            self.rt.start()
        finally:
            globals()['_ThreadingTimer'] = original

        self.assertTrue(self.rt.is_running)
        mock_timer_cls.assert_called_once_with(0.1, self.rt._run)
        mock_instance.start.assert_called_once()

    def test_start_idempotent(self):
        """Calling start() twice does not create a second timer."""
        timers_created = []

        def fake_timer(interval, fn):
            m = MagicMock()
            timers_created.append(m)
            return m

        original = globals()['_ThreadingTimer']
        globals()['_ThreadingTimer'] = fake_timer
        try:
            self.rt.start()
            self.rt.start()   # second call should be ignored
        finally:
            globals()['_ThreadingTimer'] = original
            if self.rt._timer:
                self.rt._timer.cancel()

        self.assertEqual(len(timers_created), 1)

    # ------------------------------------------------------------------
    # stop
    # ------------------------------------------------------------------

    def test_stop(self):
        """stop() cancels the timer, clears is_running, resets _start_time,
        and calls the stop callback."""
        # BUG FIX 4: Original set self.rt.is_running = True directly, which
        # works fine since is_running is a plain bool attribute (not a property).
        # Kept as-is; just verify all stop() postconditions.
        self.rt._timer     = MagicMock()
        self.rt.is_running = True

        self.rt.stop()

        self.rt._timer.cancel.assert_called_once()
        self.assertFalse(self.rt.is_running)
        self.assertEqual(self.rt._start_time, 0)
        self.mock_stop.assert_called_once()

    def test_stop_with_arguments(self):
        """stop() forwards stop_input_args and stop_input_kwargs to the callback."""
        test_args   = (1, 2, 3)
        test_kwargs = {'a': 1, 'b': 2}

        self.rt.stop_input_args   = test_args
        self.rt.stop_input_kwargs = test_kwargs

        self.rt.stop()

        self.mock_stop.assert_called_once_with(*test_args, **test_kwargs)

    def test_no_stop_function(self):
        """stop() with no stop_function set does not raise."""
        self.rt.stop_function = None
        try:
            self.rt.stop()
        except Exception as e:
            self.fail(f"stop() raised unexpected exception: {e}")

    # ------------------------------------------------------------------
    # _run cycle
    # ------------------------------------------------------------------

    def test_run_with_arguments(self):
        """timer_function is called with start_input_args / kwargs on each tick."""
        # BUG FIX 5: Original used patch('threading.Timer', side_effect=lambda i, f: f())
        # which calls f() (i.e. _run) but returns None, so self._timer = None after
        # start().  _run then tries self._timer.cancel() later, crashing with
        # AttributeError.  Use a proper mock that returns a MagicMock timer.
        test_args   = (1, 2, 3)
        test_kwargs = {'a': 1, 'b': 2}
        self.rt.start_input_args   = test_args
        self.rt.start_input_kwargs = test_kwargs

        call_count = [0]
        def fake_timer(interval, fn):
            call_count[0] += 1
            if call_count[0] == 1:
                fn()   # fire _run exactly once
            return MagicMock()

        original = globals()['_ThreadingTimer']
        globals()['_ThreadingTimer'] = fake_timer
        try:
            self.rt.start()
        finally:
            globals()['_ThreadingTimer'] = original
            self.rt.is_running = False   # prevent further rescheduling

        self.mock_callback.assert_called_once_with(*test_args, **test_kwargs)

    def test_run_cycle_respects_limit(self):
        """Timer stops automatically after the configured limit is exceeded."""
        # BUG FIX 6: Original set limit=0.3 with interval=0.1 and expected
        # ≥2 callback invocations, but the mock timer fired _run immediately
        # (before _start_time was set) causing the limit check to trigger on
        # the very first call and stopping after 0 real callbacks.
        #
        # Instead we test the limit mechanism directly: set _start_time to a
        # past moment far enough back that the limit is already exceeded on
        # the first _run call.
        self.rt.limit    = 0.3
        self.rt.interval = 0.1

        # Pretend the timer has been running for 1 second already
        self.rt.is_running  = True
        self.rt._start_time = time.time() - 1.0

        self.rt._run()

        # _run should have called stop() because limit was exceeded
        self.assertFalse(self.rt.is_running)
        self.mock_stop.assert_called_once()
        # timer_function must NOT have been called (limit hit before the call)
        self.mock_callback.assert_not_called()

    def test_run_calls_callback_when_within_limit(self):
        """_run calls timer_function when the elapsed time is within the limit."""
        self.rt.limit       = 60.0   # generous limit
        self.rt.is_running  = True
        self.rt._start_time = time.time()
        self.rt._timer      = MagicMock()   # prevent real rescheduling

        self.rt._run()

        self.mock_callback.assert_called_once()


if __name__ == '__main__':
    unittest.main()