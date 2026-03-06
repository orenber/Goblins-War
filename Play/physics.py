from Utility.timer_utility import TimerController
from Utility import is_member
import math
from typing import Optional, Callable


class PhysicsObject:
    """
    A physics-based object with movement capabilities and collision detection.

    Features:
    - 2D/3D movement with gravity
    - Customizable physics properties
    - Event callbacks for updates and stops
    - Timer-based movement control
    """

    def __init__(self, **kwargs):
        """
        Initialize the physics object with default or provided properties.

        Args:
            **kwargs: Configuration properties (see set_setup for options)
        """
        # Physical properties
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

        # Environmental boundaries
        self.bottom = 0.0
        self.surface_x = 0.0
        self.surface_y = 0.0
        self.surface_z = 0.0

        # State tracking
        self._is_stable = True
        self._elapsed_time = 0.0

        # Callbacks
        self._on_update: Optional[Callable] = None
        self._on_stop: Optional[Callable] = None

        # BUG FIX 1: TimerController was initialised with start_func pointing at
        # _update_movement, which takes (vx, vy, vz) arguments supplied later via
        # start_input_args.  However __init__ runs before throw() is ever called,
        # so those args don't exist yet.  Defer all timer configuration to throw()
        # and create the timer with no arguments here.
        self._movement_timer = TimerController(interval=self.time_step)

        # Apply any custom configuration
        self.set_setup(**kwargs)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def position(self) -> tuple:
        """Get the current (x, y, z) position as a tuple."""
        return self.x, self.y, self.z

    @property
    def velocity(self) -> tuple:
        """Get the current (vx, vy, vz) velocity as a tuple."""
        return self.velocity_x, self.velocity_y, self.velocity_z

    @property
    def is_moving(self) -> bool:
        """Check if the object is currently in motion."""
        return not self._is_stable

    @property
    def on_update(self) -> Optional[Callable]:
        return self._on_update

    @on_update.setter
    def on_update(self, callback: Optional[Callable]) -> None:
        if callback is None or callable(callback):
            self._on_update = callback

    @property
    def on_stop(self) -> Optional[Callable]:
        return self._on_stop

    @on_stop.setter
    def on_stop(self, callback: Optional[Callable]) -> None:
        if callback is None or callable(callback):
            self._on_stop = callback

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_setup(self, **properties) -> None:
        """
        Configure multiple object properties at once.

        Args:
            **properties: Key-value pairs of properties to set

        Raises:
            ValueError: If any property name is invalid
        """
        valid_properties = {
            'x', 'y', 'z', 'angle', 'velocity_x', 'velocity_y', 'velocity_z',
            'mass', 'bottom', 'gravity', 'elasticity', 'surface_x', 'surface_y',
            'surface_z', 'time_step', 'on_update', 'on_stop'
        }

        property_names = list(properties.keys())
        is_valid, invalid = is_member(property_names, valid_properties)
        if not is_valid:
            raise ValueError(f"Invalid properties: {invalid}")

        for name, value in properties.items():
            setattr(self, name, value)

        if 'time_step' in properties:
            self._movement_timer.interval = self.time_step

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def throw(self, velocity_x: float, velocity_y: float, velocity_z: float = 0) -> None:
        """
        Launch the object with specified velocities.

        Args:
            velocity_x: Horizontal velocity (x-axis)
            velocity_y: Vertical velocity (y-axis)
            velocity_z: Depth velocity (z-axis, optional)
        """
        # BUG FIX 2: The original stored the launch velocities as instance attrs
        # but _update_movement received them as positional args from start_input_args.
        # After a bounce, surface_x/y/z and _elapsed_time are reset but the timer
        # is restarted with the *original* launch velocities — so post-bounce
        # x/z positions restart from the bounce point correctly but the passed-in
        # vy is the *original* launch vy, not the reflected one.  Fix: capture
        # the current velocities as closures rather than passing them through
        # start_input_args, so that bounces naturally use the updated values.
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.velocity_z = velocity_z

        self._elapsed_time = 0.0
        self._is_stable = False

        # BUG FIX 3: Configure the timer fully here (not partially in __init__)
        # so the stop callback is always registered before the first tick.
        self._movement_timer.start_func = self._update_movement
        self._movement_timer.stop_function = self._handle_stop
        self._movement_timer.start()

    def _update_movement(self) -> None:
        """
        Update the object's position based on physics calculations.

        Uses instance velocity attributes (set by throw / bounce) rather than
        frozen constructor arguments, so post-bounce velocities are correct.
        """
        self._elapsed_time += self.time_step

        t = self._elapsed_time
        # BUG FIX 4: Kinematic equations used the *initial* vx/vy/vz from
        # start_input_args for every tick.  After a bounce the object's
        # velocity_y is negated and scaled by elasticity but the position
        # formula still used the original throw velocity, so the arc after a
        # bounce was always identical to the first one regardless of elasticity.
        # Now we integrate using the *current* velocity attributes.
        self.x = self.surface_x + self.velocity_x * t
        self.y = self.surface_y + self.velocity_y * t - 0.5 * self.gravity * t ** 2
        self.z = self.surface_z + self.velocity_z * t

        # Ground collision
        if self.y <= self.bottom:
            self.y = self.bottom

            # BUG FIX 5: The elasticity check didn't account for very small
            # bounce velocities — the ball would keep bouncing infinitely with
            # tiny, imperceptible hops.  Stop movement when the reflected
            # velocity is negligible (< 0.1 units/s after scaling).
            reflected_vy = -self.velocity_y * self.elasticity
            if self.elasticity > 0 and abs(reflected_vy) >= 0.1:
                self.velocity_y = reflected_vy
                # BUG FIX 6: surface_z was never updated on bounce, so z
                # position drifted after each bounce as it restarted from 0.
                self.surface_x = self.x
                self.surface_y = self.bottom
                self.surface_z = self.z       # ← was missing
                self._elapsed_time = 0.0
            else:
                self._movement_timer.stop()

        if callable(self._on_update):
            self._on_update(self)

    def _handle_stop(self) -> None:
        """Handle movement stopping and trigger the on_stop callback."""
        self._is_stable = True
        if callable(self._on_stop):
            self._on_stop(self)

    def stop(self) -> None:
        """Immediately stop all movement."""
        self._movement_timer.stop()


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    """Demonstration of PhysicsObject usage."""

    def log_position(obj: PhysicsObject):
        print(f"Object at X:{obj.x:.2f}, Y:{obj.y:.2f}")

    def log_stop(obj: PhysicsObject):
        print(f"Object stopped at X:{obj.x:.2f}, Y:{obj.y:.2f}")

    ball1 = PhysicsObject(
        time_step=0.01,
        gravity=9.8,
        bottom=0,
        on_update=log_position
    )

    ball2 = PhysicsObject(
        time_step=0.01,
        gravity=9.8,
        bottom=0,
        elasticity=0.7,
        on_update=log_position,
        on_stop=log_stop
    )

    ball1.throw(10, 10)
    ball2.throw(15, 10)

    try:
        while ball1.is_moving or ball2.is_moving:
            pass
    except KeyboardInterrupt:
        ball1.stop()
        ball2.stop()


if __name__ == "__main__":
    main()