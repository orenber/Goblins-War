from Utility.timer_utility import TimerController
from Utility import is_member
import math
from typing import Optional, Callable, Dict, Any


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
        self.elasticity = 0.5  # Bounciness coefficient

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

        # Movement controller
        self._movement_timer = TimerController(
            interval=self.time_step,
            start_func=self._update_movement
        )

        # Apply any custom configuration
        self.set_setup(**kwargs)

    @property
    def position(self) -> tuple:
        """Get the current (x, y, z) position as a tuple"""
        return self.x, self.y, self.z

    @property
    def velocity(self) -> tuple:
        """Get the current (vx, vy, vz) velocity as a tuple"""
        return self.velocity_x, self.velocity_y, self.velocity_z

    @property
    def is_moving(self) -> bool:
        """Check if the object is currently in motion"""
        return not self._is_stable

    @property
    def on_update(self) -> Optional[Callable]:
        """Get the current update callback function"""
        return self._on_update

    @on_update.setter
    def on_update(self, callback: Optional[Callable]) -> None:
        """Set the update callback function"""
        if callback is None or callable(callback):
            self._on_update = callback

    @property
    def on_stop(self) -> Optional[Callable]:
        """Get the current stop callback function"""
        return self._on_stop

    @on_stop.setter
    def on_stop(self, callback: Optional[Callable]) -> None:
        """Set the stop callback function"""
        if callback is None or callable(callback):
            self._on_stop = callback

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

        # Validate property names
        property_names = list(properties.keys())
        is_valid, invalid = is_member(property_names, valid_properties)
        if not is_valid:
            raise ValueError(f"Invalid properties: {invalid}")

        # Set properties
        for name, value in properties.items():
            setattr(self, name, value)

        # Update timer interval if time_step changed
        if 'time_step' in properties:
            self._movement_timer.interval = self.time_step

    def throw(self, velocity_x: float, velocity_y: float, velocity_z: float = 0) -> None:
        """
        Launch the object with specified velocities.

        Args:
            velocity_x: Horizontal velocity (x-axis)
            velocity_y: Vertical velocity (y-axis)
            velocity_z: Depth velocity (z-axis, optional)
        """
        # Set initial velocities
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.velocity_z = velocity_z

        # Reset state
        self._elapsed_time = 0.0
        self._is_stable = False

        # Configure and start movement timer
        self._movement_timer.start_input_args = (velocity_x, velocity_y, velocity_z)
        self._movement_timer.stop_function = self._handle_stop
        self._movement_timer.start()

    def _update_movement(self, velocity_x: float, velocity_y: float, velocity_z: float) -> None:
        """
        Update the object's position based on physics calculations.

        Args:
            velocity_x: Initial x velocity
            velocity_y: Initial y velocity
            velocity_z: Initial z velocity
        """
        self._elapsed_time += self.time_step

        # Update position using kinematic equations
        t = self._elapsed_time
        self.x = self.surface_x + velocity_x * t
        self.y = self.surface_y + velocity_y * t - 0.5 * self.gravity * t ** 2
        self.z = self.surface_z + velocity_z * t

        # Check for ground collision
        if self.y <= self.bottom:
            self.y = self.bottom

            # Apply bounce if object has elasticity
            if self.elasticity > 0:
                self.velocity_y = -self.velocity_y * self.elasticity
                self.surface_y = self.bottom
                self.surface_x = self.x
                self._elapsed_time = 0.0
            else:
                self._movement_timer.stop()

        # Trigger update callback
        if callable(self._on_update):
            self._on_update(self)

    def _handle_stop(self) -> None:
        """Handle movement stopping and callbacks"""
        self._is_stable = True
        if callable(self._on_stop):
            self._on_stop(self)

    def stop(self) -> None:
        """Immediately stop all movement"""
        self._movement_timer.stop()


def main():
    """Demonstration of PhysicsObject usage"""

    def log_position(obj: PhysicsObject):
        print(f"Object at X:{obj.x:.2f}, Y:{obj.y:.2f}")

    def log_stop(obj: PhysicsObject):
        print(f"Object stopped at X:{obj.x:.2f}, Y:{obj.y:.2f}")

    # Create and configure physics objects
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
        elasticity=0.7,  # Make this ball bouncy
        on_update=log_position,
        on_stop=log_stop
    )

    # Throw the objects
    ball1.throw(10, 10)
    ball2.throw(15, 10)

    # Keep program running while objects move
    try:
        while ball1.is_moving or ball2.is_moving:
            pass
    except KeyboardInterrupt:
        ball1.stop()
        ball2.stop()


if __name__ == "__main__":
    main()