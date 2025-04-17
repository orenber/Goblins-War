import unittest
from unittest.mock import MagicMock, patch
import time
from threading import Timer
from Utility.timer_utility import TimerController, TicTocGenerator, toc, tic  # Update import path


class TestTicToc(unittest.TestCase):
    def test_tic_toc_generator(self):
        """Test the timing generator functionality"""
        gen = TicTocGenerator()
        t1 = next(gen)
        time.sleep(0.1)
        t2 = next(gen)
        self.assertGreater(t2, t1)
        self.assertAlmostEqual(t2, 0.1, delta=0.05)

    def test_toc(self):
        """Test the toc function"""
        tic()
        time.sleep(0.1)
        elapsed = toc()
        self.assertAlmostEqual(elapsed, 0.1, delta=0.05)


class TestRepeatedTimer(unittest.TestCase):
    def setUp(self):
        self.mock_callback = MagicMock()
        self.mock_stop = MagicMock()
        self.rt = TimerController(interval=0.1)
        self.rt.timer_function = self.mock_callback
        self.rt.stop_function = self.mock_stop

    def test_initialization(self):
        """Test default initialization values"""
        self.assertEqual(self.rt.interval, 0.1)
        self.assertIsNone(self.rt._timer)
        self.assertFalse(self.rt.is_running)
        self.assertEqual(self.rt.limit, 10)

    def test_property_setters(self):
        """Test all property setters"""
        # Test start function args/kwargs
        test_args = (1, 2, 3)
        test_kwargs = {'a': 1, 'b': 2}
        self.rt.start_input_args = test_args
        self.rt.start_input_kwargs = test_kwargs
        self.assertEqual(self.rt.start_input_args, test_args)
        self.assertEqual(self.rt.start_input_kwargs, test_kwargs)

        # Test stop function args/kwargs
        self.rt.stop_input_args = test_args
        self.rt.stop_input_kwargs = test_kwargs
        self.assertEqual(self.rt.stop_input_args, test_args)
        self.assertEqual(self.rt.stop_input_kwargs, test_kwargs)

    def test_set_attr(self):
        """Test the set_attr method"""
        test_attrs = {
            'interval': 0.5,
            'timer_function': lambda: None,
            'start_input_args': (1, 2),
            'start_input_kwargs': {'x': 1},
            'stop_function': lambda: None,
            'stop_input_args': (3, 4),
            'stop_input_kwargs': {'y': 2},
            'limit': 5
        }
        self.rt.set_attr(**test_attrs)

        for attr, value in test_attrs.items():
            self.assertEqual(getattr(self.rt, attr), value)

    @patch('threading.Timer')
    def test_start(self, mock_timer):
        """Test timer start functionality"""
        self.rt.start()
        self.assertTrue(self.rt.is_running)
        mock_timer.assert_called_once_with(0.1, self.rt._run)
        mock_timer.return_value.start.assert_called_once()

    def test_stop(self):
        """Test timer stop functionality"""
        # First start the timer
        self.rt._timer = MagicMock()
        self.rt.is_running = True

        # Now stop it
        self.rt.stop()

        # Verify stop behavior
        self.rt._timer.cancel.assert_called_once()
        self.assertFalse(self.rt.is_running)
        self.assertEqual(self.rt._start_time, 0)
        self.mock_stop.assert_called_once()

    def test_run_cycle(self):
        """Test complete timer run cycle"""
        # Setup test conditions
        self.rt.interval = 0.1
        self.rt.limit = 0.3  # Should run 3 times

        # Mock the timer to call _run immediately
        original_timer = Timer

        def mock_timer(interval, function):
            function()
            return MagicMock()

        with patch('threading.Timer', side_effect=mock_timer):
            self.rt.start()

            # Allow time for execution (though mocked)
            time.sleep(0.5)

            # Verify callback was called multiple times
            self.assertGreaterEqual(self.mock_callback.call_count, 2)

            # Verify timer stopped after reaching limit
            self.assertFalse(self.rt.is_running)
            self.mock_stop.assert_called_once()

    def test_run_with_arguments(self):
        """Test timer with function arguments"""
        test_args = (1, 2, 3)
        test_kwargs = {'a': 1, 'b': 2}

        self.rt.start_input_args = test_args
        self.rt.start_input_kwargs = test_kwargs

        # Mock the timer to call _run immediately
        with patch('threading.Timer', side_effect=lambda i, f: f()):
            self.rt.start()

            # Verify callback was called with correct arguments
            self.mock_callback.assert_called_once_with(*test_args, **test_kwargs)

    def test_stop_with_arguments(self):
        """Test stop callback with arguments"""
        test_args = (1, 2, 3)
        test_kwargs = {'a': 1, 'b': 2}

        self.rt.stop_input_args = test_args
        self.rt.stop_input_kwargs = test_kwargs

        # Stop the timer
        self.rt.stop()

        # Verify stop callback was called with correct arguments
        self.mock_stop.assert_called_once_with(*test_args, **test_kwargs)

    def test_no_stop_function(self):
        """Test behavior when no stop function is set"""
        self.rt.stop_function = None
        try:
            self.rt.stop()
        except Exception as e:
            self.fail(f"stop() raised unexpected exception: {e}")


if __name__ == '__main__':
    unittest.main()