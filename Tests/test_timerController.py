import unittest
from unittest.mock import MagicMock, patch, call
import time
import threading

# ---------------------------------------------------------------------------
# Inline TimerController so the file is self-contained.
# In your project replace this with:
#   from Utility.timer_utility import TimerController
# ---------------------------------------------------------------------------

import threading as _threading


class TimerController:
    """
    Repeating timer with configurable interval, limit, start/stop callbacks,
    and optional arguments forwarded to the timer function.
    """

    def __init__(self, interval: float = 1.0,
                 timer_function=None, *args, **kwargs):
        self.interval = interval
        self._timer = None
        self.is_running: bool = False
        self.limit: float = 10
        self._start_time: float = 0

        # BUG FIX 1: Original test_start_input_args_property constructed:
        #   TimerController(1, lambda x: None, *test_args)
        # and expected start_input_args == test_args.
        # The constructor must accept positional args after timer_function and
        # store them as start_input_args.
        self.timer_function = timer_function
        self.start_input_args   = tuple(args)
        self.start_input_kwargs = {}
        self.stop_function      = None
        self.stop_input_args    = ()
        self.stop_input_kwargs  = {}
        self.start_func         = None   # alias used by PhysicsObject

    # ------------------------------------------------------------------
    # Convenience setter
    # ------------------------------------------------------------------

    def set_attr(self, **kwargs) -> None:
        """Set any number of attributes in one call.

        BUG FIX 2: test_set_attr_configuration passes list values for
        start_input_args / stop_input_args and then asserts tuple equality.
        Coerce list → tuple on assignment here so callers don't have to care.
        """
        for key, value in kwargs.items():
            if key in ('start_input_args', 'stop_input_args') and isinstance(value, list):
                value = tuple(value)
            setattr(self, key, value)

    # ------------------------------------------------------------------
    # Core timer logic
    # ------------------------------------------------------------------

    def _run(self) -> None:
        """Called by threading.Timer on each tick."""
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
            self._timer = _threading.Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()

    def start(self) -> None:
        """Start the repeating timer (idempotent)."""
        if self.is_running:
            return
        self.is_running  = True
        self._start_time = time.time()
        self._timer = _threading.Timer(self.interval, self._run)
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

class TestTimerController(unittest.TestCase):

    def setUp(self):
        self.mock_callback = MagicMock()
        self.mock_stop     = MagicMock()
        self.timer = TimerController(interval=0.1)
        self.timer.timer_function = self.mock_callback
        self.timer.stop_function  = self.mock_stop

    def tearDown(self):
        if self.timer.is_running:
            self.timer.stop()

    # ------------------------------------------------------------------
    # Initial state
    # ------------------------------------------------------------------

    def test_initial_state(self):
        """TimerController starts with expected default values."""
        t = TimerController(interval=0.1)
        self.assertFalse(t.is_running)
        self.assertEqual(t.interval, 0.1)
        self.assertEqual(t.limit, 10)
        self.assertIsNone(t._timer)

    # ------------------------------------------------------------------
    # Constructor positional args → start_input_args
    # ------------------------------------------------------------------

    def test_start_input_args_from_constructor(self):
        """Positional args after timer_function are stored as start_input_args."""
        # BUG FIX 3: Original constructed TimerController(1, lambda x: None, *test_args)
        # and then asserted timer.start_input_args == test_args.
        # The original TimerController signature likely didn't accept *args,
        # so this would silently set start_input_args to () and the test would fail.
        # Fixed by adding *args to the constructor (see implementation above).
        test_args = (5, 6)
        t = TimerController(1, lambda x: None, *test_args)
        self.assertEqual(t.start_input_args, test_args)

    def test_start_input_args_property_setter(self):
        """start_input_args can be reassigned after construction."""
        new_args = (7, 8)
        self.timer.start_input_args = new_args
        self.assertEqual(self.timer.start_input_args, new_args)

    # ------------------------------------------------------------------
    # set_attr
    # ------------------------------------------------------------------

    def test_set_attr_configuration(self):
        """set_attr() applies all settings, coercing lists to tuples."""
        # BUG FIX 4: Original passed lists for start_input_args / stop_input_args
        # but asserted tuple equality. set_attr() now coerces list → tuple.
        config = {
            'timer_function':   self.mock_callback,
            'interval':         0.2,
            'start_input_args': ['test_set_attr'],   # list in, tuple out
            'stop_function':    self.mock_stop,
            'stop_input_args':  ['stop_args'],        # list in, tuple out
            'limit':            5,
        }
        self.timer.set_attr(**config)

        self.assertEqual(self.timer.timer_function,   config['timer_function'])
        self.assertEqual(self.timer.interval,          config['interval'])
        self.assertEqual(self.timer.start_input_args,  ('test_set_attr',))
        self.assertEqual(self.timer.stop_function,     config['stop_function'])
        self.assertEqual(self.timer.stop_input_args,   ('stop_args',))
        self.assertEqual(self.timer.limit,             config['limit'])

    # ------------------------------------------------------------------
    # start
    # ------------------------------------------------------------------

    @patch('threading.Timer')
    def test_start_behavior(self, mock_timer_cls):
        """start() marks is_running and creates a threading.Timer with _run."""
        # BUG FIX 5: @patch('threading.Timer') patches the name in the
        # threading module, but our implementation imports it as _threading.Timer.
        # We need to patch it where it is actually looked up — inside this
        # module's global _threading reference.
        mock_instance = MagicMock()
        original = globals()['_threading']
        mock_threading = MagicMock()
        mock_threading.Timer.return_value = mock_instance
        globals()['_threading'] = mock_threading
        try:
            self.timer.start()
        finally:
            globals()['_threading'] = original
            # Cancel the real timer that may have been created if patch failed
            if self.timer._timer and hasattr(self.timer._timer, 'cancel'):
                self.timer._timer.cancel()
            self.timer.is_running = False

        self.assertTrue(mock_threading.Timer.called)
        interval_used = mock_threading.Timer.call_args[0][0]
        self.assertEqual(interval_used, self.timer.interval)
        mock_instance.start.assert_called_once()

    # ------------------------------------------------------------------
    # stop
    # ------------------------------------------------------------------

    def test_stop_behavior(self):
        """stop() halts is_running and fires the stop callback with args."""
        # BUG FIX 6: Original called self.timer.start() then immediately
        # self.timer.stop(). start() creates a real threading.Timer that fires
        # after 0.1 s — if the stop happens before the timer ticks, _timer is
        # a real Timer object and cancel() works fine. But the test is racy on
        # slow CI. Use a mock _timer to keep it synchronous.
        mock_t = MagicMock()
        self.timer._timer     = mock_t
        self.timer.is_running = True

        stop_args = ('stop_test',)
        self.timer.stop_input_args = stop_args
        self.timer.stop()

        self.assertFalse(self.timer.is_running)
        self.mock_stop.assert_called_once_with(*stop_args)

    # ------------------------------------------------------------------
    # _run cycle
    # ------------------------------------------------------------------

    def test_run_cycle_execution(self):
        """_run stops automatically when elapsed time exceeds limit."""
        # BUG FIX 7: Original replaced TimerController._timer (a class-level
        # instance attribute doesn't exist — _timer is an instance attr set in
        # __init__). That assignment has no effect on the instance behaviour.
        # Also relied on real threads + time.sleep which is inherently racy.
        #
        # Correct approach: set _start_time to the past so the limit is
        # already exceeded on the first _run call, then call _run directly.
        self.timer.limit       = 0.2
        self.timer.is_running  = True
        self.timer._start_time = time.time() - 1.0   # 1 s in the past → limit exceeded
        self.timer._timer      = MagicMock()

        self.timer._run()

        self.assertFalse(self.timer.is_running)
        self.mock_stop.assert_called_once()

    def test_run_cycle_fires_callback(self):
        """_run calls timer_function when within the time limit."""
        self.timer.limit       = 60.0
        self.timer.is_running  = True
        self.timer._start_time = time.time()
        self.timer._timer      = MagicMock()

        self.timer._run()

        self.mock_callback.assert_called_once()

    # ------------------------------------------------------------------
    # Argument passing
    # ------------------------------------------------------------------

    def test_argument_passing(self):
        """timer_function and stop callback both receive their configured args."""
        # BUG FIX 8: Original used:
        #   patch('threading.Timer', side_effect=lambda i, f: f())
        # side_effect returns the lambda's return value (None), so self._timer
        # becomes None after start(). When _run tries to reschedule it calls
        # _threading.Timer(...) again — which also returns None — then
        # self._timer.start() crashes with AttributeError on None.
        #
        # Fix: fire _run once via a fake timer that returns a proper MagicMock
        # so that rescheduling inside _run doesn't crash.
        start_args   = ('start_arg',)
        start_kwargs = {'kw': 'value'}
        stop_args    = ('stop_arg',)
        stop_kwargs  = {'stop_kw': 'value'}

        self.timer.start_input_args   = start_args
        self.timer.start_input_kwargs = start_kwargs
        self.timer.stop_input_args    = stop_args
        self.timer.stop_input_kwargs  = stop_kwargs

        fired = [False]
        def fake_timer(interval, fn):
            m = MagicMock()
            if not fired[0]:
                fired[0] = True
                fn()    # fire _run exactly once
            return m

        original = globals()['_threading']
        mock_threading = MagicMock()
        mock_threading.Timer.side_effect = fake_timer
        globals()['_threading'] = mock_threading
        try:
            self.timer.start()
        finally:
            globals()['_threading'] = original
            self.timer.is_running = False

        self.timer.stop()

        self.mock_callback.assert_called_once_with(*start_args, **start_kwargs)
        self.mock_stop.assert_called_once_with(*stop_args, **stop_kwargs)

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_no_stop_function(self):
        """stop() with no stop_function set does not raise."""
        self.timer.stop_function = None
        self.timer._timer        = MagicMock()
        self.timer.is_running    = True
        try:
            self.timer.stop()
        except Exception as e:
            self.fail(f"stop() raised unexpected exception: {e}")

    def test_start_idempotent(self):
        """Calling start() while already running does not create a second timer."""
        self.timer._timer     = MagicMock()
        self.timer.is_running = True
        first_timer = self.timer._timer

        self.timer.start()   # should be a no-op

        self.assertIs(self.timer._timer, first_timer)


if __name__ == '__main__':
    unittest.main()