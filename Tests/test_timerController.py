import unittest
from unittest.mock import MagicMock, patch
import time
from Utility.timer_utility import TimerController  # Update with your import path


class TestTimerController(unittest.TestCase):
    def setUp(self):
        """Initialize test fixtures"""
        self.mock_callback = MagicMock()
        self.mock_stop = MagicMock()
        self.timer = TimerController(interval=0.1)  # Short interval for faster tests
        self.timer.timer_function = self.mock_callback
        self.timer.stop_function = self.mock_stop

    def tearDown(self):
        """Clean up after each test"""
        if self.timer.is_running:
            self.timer.stop()

    def test_initial_state(self):
        """Test initial timer state"""
        self.assertFalse(self.timer.is_running)
        self.assertEqual(self.timer.interval, 0.1)
        self.assertEqual(self.timer.limit, 10)
        self.assertIsNone(self.timer._timer)

    def test_start_input_args_property(self):
        """Test start_input_args property"""
        # Test constructor args
        test_args = (5, 6)
        timer = TimerController(1, lambda x: None, *test_args)
        self.assertEqual(timer.start_input_args, test_args)

        # Test property setter
        new_args = (7, 8)
        self.timer.start_input_args = new_args
        self.assertEqual(self.timer.start_input_args, new_args)

    def test_set_attr_configuration(self):
        """Test comprehensive configuration via set_attr"""
        config = {
            'timer_function': self.mock_callback,
            'interval': 0.2,
            'start_input_args': ['test_set_attr'],
            'stop_function': self.mock_stop,
            'stop_input_args': ['stop_args'],
            'limit': 5
        }

        self.timer.set_attr(**config)

        # Verify all configurations were set
        self.assertEqual(self.timer.timer_function, config['timer_function'])
        self.assertEqual(self.timer.interval, config['interval'])
        self.assertEqual(self.timer.start_input_args, tuple(config['start_input_args']))
        self.assertEqual(self.timer.stop_function, config['stop_function'])
        self.assertEqual(self.timer.stop_input_args, tuple(config['stop_input_args']))
        self.assertEqual(self.timer.limit, config['limit'])

    @patch('threading.Timer')
    def test_start_behavior(self, mock_timer):
        """Test timer start functionality"""
        # Configure test
        test_args = ('test_start',)
        self.timer.start_input_args = test_args

        # Start the timer
        self.timer.start()

        # Verify state
        self.assertTrue(self.timer.is_running)
        mock_timer.assert_called_once_with(
            self.timer.interval,
            self.timer._run
        )
        mock_timer.return_value.start.assert_called_once()

    def test_stop_behavior(self):
        """Test timer stop functionality"""
        # Start the timer first
        self.timer.start()
        self.assertTrue(self.timer.is_running)

        # Set stop arguments
        stop_args = ('stop_test',)
        self.timer.stop_input_args = stop_args

        # Stop the timer
        self.timer.stop()

        # Verify state and calls
        self.assertFalse(self.timer.is_running)
        self.mock_stop.assert_called_once_with(*stop_args)

    def test_run_cycle_execution(self):
        """Test complete timer cycle execution"""
        # Configure for quick test
        self.timer.interval = 0.05
        self.timer.limit = 0.2  # Should run about 4 times

        # Replace actual Timer with immediate execution
        original_timer = TimerController._timer

        def mock_timer(interval, func):
            func()  # Execute immediately
            return MagicMock()

        TimerController._timer = mock_timer
        try:
            self.timer.start()
            time.sleep(0.3)  # Allow time for execution

            # Verify callback was called multiple times
            self.assertGreaterEqual(self.mock_callback.call_count, 2)

            # Verify timer stopped after reaching limit
            self.assertFalse(self.timer.is_running)
            self.mock_stop.assert_called_once()
        finally:
            TimerController._timer = original_timer

    def test_argument_passing(self):
        """Test argument passing to callbacks"""
        # Set up test arguments
        start_args = ('start_arg',)
        start_kwargs = {'kw': 'value'}
        stop_args = ('stop_arg',)
        stop_kwargs = {'stop_kw': 'value'}

        self.timer.start_input_args = start_args
        self.timer.start_input_kwargs = start_kwargs
        self.timer.stop_input_args = stop_args
        self.timer.stop_input_kwargs = stop_kwargs

        # Mock the timer to call _run immediately
        with patch('threading.Timer', side_effect=lambda i, f: f()):
            self.timer.start()
            self.timer.stop()

            # Verify arguments were passed correctly
            self.mock_callback.assert_called_once_with(*start_args, **start_kwargs)
            self.mock_stop.assert_called_once_with(*stop_args, **stop_kwargs)

    def test_no_stop_function(self):
        """Test behavior when no stop function is set"""
        self.timer.stop_function = None
        self.timer.start()

        # Should stop without errors
        try:
            self.timer.stop()
        except Exception as e:
            self.fail(f"stop() raised unexpected exception: {e}")


if __name__ == '__main__':
    unittest.main()