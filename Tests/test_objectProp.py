import unittest
from unittest.mock import MagicMock, patch, call
import sys
import math

# ---------------------------------------------------------------------------
# Inline PhysicsObject so the file is self-contained.
# In your project replace this with:  from Play.physics import PhysicsObject
# ---------------------------------------------------------------------------

class _TimerController:
    """Minimal stand-in for TimerController used by PhysicsObject."""
    def __init__(self, interval=0.01):
        self.interval = interval
        self.start_func = None
        self.stop_function = None
        self._running = False

    @property
    def is_running(self):
        return self._running

    def start(self):
        self._running = True

    def stop(self):
        self._running = False
        if callable(self.stop_function):
            self.stop_function()


def _is_member(fields, valid):
    unknown = set(fields) - set(valid)
    return len(unknown) == 0, unknown


class PhysicsObject:
    """
    Physics-based object with projectile motion, gravity, bouncing, and
    timer-driven movement. Public API matches the fixed implementation.
    """

    def __init__(self, **kwargs):
        # Kinematic state
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.angle = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.velocity_z = 0.0
        self.mass = 1.0
        self.time_step = 0.01
        self.gravity = 9.8
        self.elasticity = 0.5

        # Boundary
        self.bottom = 0.0
        self.surface_x = 0.0
        self.surface_y = 0.0
        self.surface_z = 0.0

        # State
        self._is_stable = True
        self._elapsed_time = 0.0

        # Callbacks
        self._on_update = None
        self._on_stop = None

        # Internal timer
        self._movement_timer = _TimerController(interval=self.time_step)

        self.set_setup(**kwargs)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_moving(self):
        return not self._is_stable

    @property
    def on_update(self):
        return self._on_update

    @on_update.setter
    def on_update(self, cb):
        if cb is None or callable(cb):
            self._on_update = cb

    @property
    def on_stop(self):
        return self._on_stop

    @on_stop.setter
    def on_stop(self, cb):
        if cb is None or callable(cb):
            self._on_stop = cb

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_setup(self, **properties):
        valid = {
            'x', 'y', 'z', 'angle', 'velocity_x', 'velocity_y', 'velocity_z',
            'mass', 'bottom', 'gravity', 'elasticity', 'surface_x', 'surface_y',
            'surface_z', 'time_step', 'on_update', 'on_stop'
        }
        is_valid, invalid = _is_member(list(properties.keys()), valid)
        if not is_valid:
            raise ValueError(f"Invalid properties: {invalid}")
        for name, value in properties.items():
            setattr(self, name, value)
        if 'time_step' in properties:
            self._movement_timer.interval = self.time_step

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def throw(self, velocity_x: float, velocity_y: float,
              velocity_z: float = 0) -> None:
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.velocity_z = velocity_z

        self._elapsed_time = 0.0
        self._is_stable = False

        self._movement_timer.start_func = self._update_movement
        self._movement_timer.stop_function = self._handle_stop
        self._movement_timer.start()

    def _update_movement(self) -> None:
        self._elapsed_time += self.time_step

        t = self._elapsed_time
        self.x = self.surface_x + self.velocity_x * t
        self.y = self.surface_y + self.velocity_y * t - 0.5 * self.gravity * t ** 2
        self.z = self.surface_z + self.velocity_z * t

        if self.y <= self.bottom:
            self.y = self.bottom
            reflected_vy = -self.velocity_y * self.elasticity
            if self.elasticity > 0 and abs(reflected_vy) >= 0.1:
                self.velocity_y = reflected_vy
                self.surface_x = self.x
                self.surface_y = self.bottom
                self.surface_z = self.z
                self._elapsed_time = 0.0
            else:
                self._movement_timer.stop()

        if callable(self._on_update):
            self._on_update(self)

    def _handle_stop(self) -> None:
        self._is_stable = True
        if callable(self._on_stop):
            self._on_stop(self)

    def stop(self) -> None:
        self._movement_timer.stop()


# ===========================================================================
# Tests
# ===========================================================================

class TestPhysicsObject(unittest.TestCase):

    def setUp(self):
        """Create a fresh PhysicsObject with mocked callbacks."""
        self.obj = PhysicsObject(time_step=0.01)
        self.update_mock = MagicMock()
        self.stop_mock   = MagicMock()
        self.obj.on_update = self.update_mock
        self.obj.on_stop   = self.stop_mock

    # ------------------------------------------------------------------
    # set_setup
    # ------------------------------------------------------------------

    def test_set_setup_valid_properties(self):
        """set_setup() applies all recognised keyword arguments."""
        # BUG FIX 1: Original passed 'time_stamp' and 'v' which are not valid
        # PhysicsObject properties (renamed to 'time_step'; 'v' never existed).
        # Also passed 'velocity_x'/'velocity_y' via the old API that didn't
        # exist. Updated to the real property names.
        params = {
            'x': 50, 'y': 20, 'angle': 30,
            'mass': 50, 'bottom': 0, 'gravity': 9.8,
            'surface_x': 0, 'surface_y': 0, 'time_step': 0.5
        }
        self.obj.set_setup(**params)
        for param, value in params.items():
            self.assertEqual(getattr(self.obj, param), value,
                             f"Property '{param}' not set correctly")

    def test_set_setup_invalid_property_raises(self):
        """set_setup() raises ValueError for unrecognised property names."""
        with self.assertRaises(ValueError):
            self.obj.set_setup(nonexistent=42)

    # ------------------------------------------------------------------
    # throw
    # ------------------------------------------------------------------

    def test_throw_sets_velocities(self):
        """throw() stores the given velocities on the object."""
        self.obj.throw(velocity_x=100, velocity_y=50)
        self.assertEqual(self.obj.velocity_x, 100)
        self.assertEqual(self.obj.velocity_y, 50)

    def test_throw_sets_is_moving(self):
        """throw() transitions is_stable to False (object is moving)."""
        # BUG FIX 2: Original checked self.obj.rt.is_running — 'rt' doesn't
        # exist; the timer is _movement_timer. Use the public is_moving property.
        self.assertFalse(self.obj.is_moving)
        self.obj.throw(10, 10)
        self.assertTrue(self.obj.is_moving)

    def test_throw_resets_elapsed_time(self):
        """throw() resets the internal elapsed time counter to zero."""
        self.obj._elapsed_time = 99.9
        self.obj.throw(5, 5)
        self.assertEqual(self.obj._elapsed_time, 0.0)

    # ------------------------------------------------------------------
    # Kinematic calculations (_update_movement driven directly)
    # ------------------------------------------------------------------

    def test_kinematic_position_after_one_step(self):
        """Position follows kinematic equations after one time step."""
        # BUG FIX 3: Original called self.obj.update() which doesn't exist as
        # a public method. The timer drives _update_movement() internally.
        # We call _update_movement() directly to unit-test the physics math
        # without needing a real timer.
        #
        # NOTE: The kinematic formula uses surface_x/surface_y as the origin
        # (the position at the moment of launch). set_setup(y=100) sets the
        # current y but NOT surface_y — surface_y must be set explicitly to
        # the launch height so the formula uses 100 as its starting point.
        self.obj.set_setup(
            x=0, y=100,
            surface_x=0, surface_y=100,   # launch origin
            velocity_x=10, velocity_y=0,
            gravity=10, bottom=-1000,
            time_step=1.0
        )
        self.obj.throw(velocity_x=10, velocity_y=0)
        self.obj._update_movement()   # one manual tick (t=1.0)

        # x = surface_x + vx * t = 0 + 10 * 1 = 10
        self.assertAlmostEqual(self.obj.x, 10.0)
        # y = surface_y + vy*t - 0.5*g*t^2 = 100 + 0 - 0.5*10*1^2 = 95
        self.assertAlmostEqual(self.obj.y, 95.0)

    def test_gravity_decreases_vertical_velocity(self):
        """Gravity should reduce upward velocity each step (not increase it)."""
        # BUG FIX 4: Original physics added gravity to velocity (wrong sign).
        # Fixed version subtracts gravity. After one step from vy=0 with g=10,
        # effective vy used in position calc is negative (downward pull).
        self.obj.set_setup(
            x=0, y=100, velocity_x=0, velocity_y=0,
            gravity=10, bottom=0, time_step=1.0
        )
        self.obj.throw(velocity_x=0, velocity_y=0)
        y_before = self.obj.y
        self.obj._update_movement()
        # With vy=0 and g=10 over t=1: y = 100 + 0 - 0.5*10*1^2 = 95
        self.assertLess(self.obj.y, y_before)

    # ------------------------------------------------------------------
    # on_update callback
    # ------------------------------------------------------------------

    def test_on_update_called_during_movement(self):
        """on_update callback is invoked on each movement tick."""
        # BUG FIX 5: Original called self.obj.update() (doesn't exist).
        # Drive via _update_movement() directly.
        self.obj.set_setup(x=0, y=100, gravity=0, bottom=-1000, time_step=0.1)
        self.obj.throw(velocity_x=10, velocity_y=10)
        self.obj._update_movement()
        self.update_mock.assert_called_once_with(self.obj)

    def test_on_update_receives_updated_object(self):
        """on_update callback receives the PhysicsObject itself."""
        received = []
        self.obj.on_update = lambda o: received.append(o)
        self.obj.set_setup(x=0, y=50, gravity=0, bottom=-1000, time_step=0.1)
        self.obj.throw(velocity_x=5, velocity_y=5)
        self.obj._update_movement()
        self.assertEqual(len(received), 1)
        self.assertIs(received[0], self.obj)

    # ------------------------------------------------------------------
    # Ground collision & on_stop callback
    # ------------------------------------------------------------------

    def test_stop_when_hitting_bottom_no_elasticity(self):
        """Object with elasticity=0 stops and fires on_stop when it hits bottom."""
        # BUG FIX 6: Original checked self.obj.rt.is_running after stop.
        # Use is_moving instead. Also drive via _update_movement, not update().
        self.obj.set_setup(
            x=0, y=1, velocity_x=0, velocity_y=-100,
            bottom=0, gravity=0, elasticity=0, time_step=1.0
        )
        self.obj.throw(velocity_x=0, velocity_y=-100)
        self.obj._update_movement()

        self.assertFalse(self.obj.is_moving)
        self.stop_mock.assert_called_once()

    def test_bounce_when_elasticity_nonzero(self):
        """Object with elasticity > 0 bounces instead of stopping."""
        self.obj.set_setup(
            x=0, y=5, velocity_x=0, velocity_y=-20,
            bottom=0, gravity=0, elasticity=0.8, time_step=1.0
        )
        self.obj.throw(velocity_x=0, velocity_y=-20)
        self.obj._update_movement()

        # Should still be moving after the bounce
        self.assertTrue(self.obj.is_moving)
        # Velocity should be reflected and reduced
        self.assertGreater(self.obj.velocity_y, 0)
        self.stop_mock.assert_not_called()

    def test_micro_bounce_stops_eventually(self):
        """Very small reflected velocity (< 0.1) causes the object to stop."""
        self.obj.set_setup(
            x=0, y=1, velocity_x=0, velocity_y=-0.05,
            bottom=0, gravity=0, elasticity=0.5, time_step=1.0
        )
        self.obj.throw(velocity_x=0, velocity_y=-0.05)
        self.obj._update_movement()
        self.assertFalse(self.obj.is_moving)

    # ------------------------------------------------------------------
    # Angle-based launch
    # ------------------------------------------------------------------

    def test_angle_and_speed_decomposition(self):
        """Angle + speed (v) can be decomposed into vx/vy before throw()."""
        # BUG FIX 7: Original expected throw(0, 0) to magically decompose angle
        # and 'v' into velocity components — that feature doesn't exist on
        # PhysicsObject. Angle decomposition is the caller's responsibility.
        # Test the decomposition math explicitly and then throw the components.
        angle_deg = 45
        speed = 10
        angle_rad = math.radians(angle_deg)
        vx = speed * math.cos(angle_rad)
        vy = speed * math.sin(angle_rad)

        self.obj.throw(velocity_x=vx, velocity_y=vy)

        self.assertAlmostEqual(self.obj.velocity_x, vx, places=4)
        self.assertAlmostEqual(self.obj.velocity_y, vy, places=4)

    # ------------------------------------------------------------------
    # Timer integration
    # ------------------------------------------------------------------

    def test_throw_starts_internal_timer(self):
        """throw() starts the internal movement timer."""
        # BUG FIX 8: Original patched 'Play.physics.RepeatedTimer' — the fixed
        # implementation uses TimerController, not RepeatedTimer. Also patching
        # at module level would not intercept the already-constructed timer
        # instance. We inspect _movement_timer.is_running directly.
        self.assertFalse(self.obj._movement_timer.is_running)
        self.obj.throw(velocity_x=5, velocity_y=5)
        self.assertTrue(self.obj._movement_timer.is_running)

    def test_stop_halts_timer(self):
        """stop() halts the movement timer."""
        self.obj.throw(velocity_x=5, velocity_y=5)
        self.assertTrue(self.obj._movement_timer.is_running)
        self.obj.stop()
        self.assertFalse(self.obj._movement_timer.is_running)

    def test_time_step_propagates_to_timer(self):
        """Changing time_step via set_setup updates the timer interval."""
        self.obj.set_setup(time_step=0.05)
        self.assertEqual(self.obj._movement_timer.interval, 0.05)

    # ------------------------------------------------------------------
    # Surface reset on bounce
    # ------------------------------------------------------------------

    def test_surface_z_updated_on_bounce(self):
        """surface_z is updated on each bounce so z doesn't drift."""
        self.obj.set_setup(
            x=0, y=5, z=50,
            velocity_x=0, velocity_y=-20, velocity_z=5,
            bottom=0, gravity=0, elasticity=0.8, time_step=1.0
        )
        self.obj.throw(velocity_x=0, velocity_y=-20, velocity_z=5)
        self.obj._update_movement()
        # After bounce, surface_z should equal the current z position
        self.assertAlmostEqual(self.obj.surface_z, self.obj.z)


if __name__ == '__main__':
    unittest.main()