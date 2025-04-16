import unittest
from unittest.mock import MagicMock, patch
from Play.physics import PhysicsObject  # Update with your actual import path


class TestObjectProp(unittest.TestCase):
    def setUp(self):
        """Initialize test object with default parameters"""
        self.obj = PhysicsObject(time_stamp=0.01)
        # Mock callbacks
        self.update_mock = MagicMock()
        self.stop_mock = MagicMock()
        self.obj.command_update = self.update_mock
        self.obj.command_stop = self.stop_mock

    def test_set_setup(self):
        """Test setting up object properties"""
        test_params = {
            'x': 50, 'y': 20, 'angle': 30, 'v': 90, 'mass': 50,
            'bottom': 0, 'gravity': 9.8, 'surface_x': 0, 'surface_y': 0,
            'time_stamp': 0.5
        }

        self.obj.set_setup(**test_params)

        # Verify all properties were set correctly
        for param, value in test_params.items():
            self.assertEqual(getattr(self.obj, param), value,
                             f"{param} not set correctly")

    def test_throw(self):
        """Test throwing the object with initial velocities"""
        # Setup initial state
        self.obj.set_setup(x=0, y=0, bottom=0, gravity=9.8)

        # Test throw
        vel_y, vel_x = 50, 100
        self.obj.throw(vel_y, vel_x)

        # Verify velocities were set
        self.assertEqual(self.obj.velocity_x, vel_x)
        self.assertEqual(self.obj.velocity_y, vel_y)

        # Verify timer was started
        self.assertTrue(hasattr(self.obj, 'rt'))
        self.assertTrue(self.obj.rt.is_running)

    def test_command_callbacks(self):
        """Test that callbacks are properly called during update"""
        # Setup test object
        self.obj.set_setup(x=0, y=0, bottom=0, gravity=0)  # No gravity for simpler test
        self.obj.throw(10, 10)  # Initial velocity

        # Simulate update
        self.obj.update()

        # Verify update callback was called
        self.update_mock.assert_called_once_with(self.obj)

        # Simulate hitting bottom
        self.obj.y = -1  # Below bottom
        self.obj.update()

        # Verify stop callback was called
        self.stop_mock.assert_called_once_with(self.obj)

    def test_movement_calculations(self):
        """Test physics calculations during movement"""
        # Setup with known parameters
        self.obj.set_setup(
            x=0, y=100,
            velocity_x=10, velocity_y=0,
            gravity=10,
            bottom=0,
            time_stamp=1.0  # Large timestep for clear changes
        )

        # First update
        self.obj.update()

        # Verify position changed
        self.assertAlmostEqual(self.obj.x, 10)  # x = x0 + vx*t
        self.assertAlmostEqual(self.obj.y, 95)  # y = y0 + vy*t - 0.5*g*t^2

        # Verify velocity changed (due to gravity)
        self.assertAlmostEqual(self.obj.velocity_y, -10)  # vy = vy0 - g*t

    def test_stop_conditions(self):
        """Test that object stops when hitting boundaries"""
        # Setup to hit bottom on first update
        self.obj.set_setup(
            x=0, y=1,
            velocity_y=-2,
            bottom=0,
            gravity=9.8,
            time_stamp=1.0
        )

        # Update should trigger stop
        self.obj.update()

        # Verify stop was called
        self.stop_mock.assert_called_once()

        # Verify timer was stopped
        self.assertFalse(self.obj.rt.is_running)

    def test_angle_calculation(self):
        """Test movement with angle initialization"""
        self.obj.set_setup(
            x=0, y=0,
            angle=45,  # 45 degree angle
            v=10,  # Initial velocity
            gravity=0,  # No gravity for simpler test
            time_stamp=1.0
        )

        # Convert angle and velocity to x,y components
        expected_vx = 10 * 0.7071  # 10 * cos(45°)
        expected_vy = 10 * 0.7071  # 10 * sin(45°)

        self.obj.throw(0, 0)  # Uses angle and v

        # Verify velocities
        self.assertAlmostEqual(self.obj.velocity_x, expected_vx, places=4)
        self.assertAlmostEqual(self.obj.velocity_y, expected_vy, places=4)

    @patch('Play.physics.RepeatedTimer')
    def test_timer_initialization(self, mock_timer):
        """Test that timer is properly initialized"""
        test_time_stamp = 0.1
        obj = PhysicsObject(time_stamp=test_time_stamp)
        obj.set_setup(x=0, y=0)
        obj.throw(10, 10)

        # Verify timer was created with correct interval
        mock_timer.assert_called_once_with(
            interval=test_time_stamp,
            function=obj.update
        )


if __name__ == '__main__':
    unittest.main()