import pygame
import os
from typing import Dict, List, Tuple, Optional, Union
from Play.physics import PhysicsObject
from Play.weapons import Gun
from Utility import is_member, Direction, full_file
from Utility.timer_utility import TimerController


class Human:
    """Base class for humanoid characters in the game."""

    def __init__(self, environment, **attr):
        """
        Initialize a human character.

        Args:
            environment: The game environment/window
            **attr: Additional attributes to set during initialization
        """
        # Private attributes
        self._environment = environment
        self._frame_count = 0
        self._size_factor = 1 / 3
        self._is_jump = False
        self._health = 100
        self._live = True

        # Character properties
        self.power = 20
        self.high = 180  # Will be scaled by _size_factor
        self.width = 60  # Will be scaled by _size_factor
        self.position_x = 200
        self.position_y = 0
        self.position_z = 0

        # Movement and state
        self.jump_count = 10
        self.move_direction = 'center'
        self.walk_direction = 'right'

        # Physics and combat
        self.physics_state = PhysicsObject()
        self.physics_state.command_update = lambda prop: self.update_position(prop)
        self.weapon = Gun(environment)

        # Resources
        self.images_path = full_file(['Resources', 'images', 'Hero'])
        self.sound_hit = full_file(['Resources', 'sound', 'hit.mp3'])

        # Animation surfaces
        self.walk_right: List[pygame.Surface] = []
        self.walk_left: List[pygame.Surface] = []
        self.standing: List[pygame.Surface] = []

        # Initialize hitbox and setup
        self.hitbox = self._update_hitbox()
        self.set_setup(**attr)
        self.create()

    def set_setup(self, **prop) -> None:
        """
        Set up character properties from keyword arguments.

        Args:
            **prop: Properties to set (position_x, position_y, high, width, walk_direction)
        """
        required = ['position_x', 'position_y', 'high', 'width', 'walk_direction']
        fields = list(prop.keys())
        (state, missing) = is_member(fields, required)

        if not state:
            raise ValueError(f'Missing required attributes: {missing}')

        for name, value in prop.items():
            setattr(self, name, value)

    @property
    def live(self) -> bool:
        """Check if the character is alive."""
        self._live = self.health > 0
        return self._live

    @property
    def high(self) -> int:
        """Get the scaled height of the character."""
        return int(self._high * self._size_factor)

    @high.setter
    def high(self, value: int) -> None:
        """Set the base height of the character."""
        self._high = value

    @property
    def width(self) -> int:
        """Get the scaled width of the character."""
        return int(self._width * self._size_factor)

    @width.setter
    def width(self, value: int) -> None:
        """Set the base width of the character."""
        self._width = value

    @property
    def position_y(self) -> int:
        """Get the current y-position."""
        return self._position_y

    @position_y.setter
    def position_y(self, value: int) -> None:
        """Set the y-position with bounds checking."""
        if value < 0 and self.health > 0:
            value = 0
        self._position_y = self.high + value
        self._update_hitbox()

    @property
    def health(self) -> int:
        """Get current health."""
        return self._health

    @health.setter
    def health(self, value: int) -> None:
        """Set health with bounds checking."""
        self._health += value
        if self._health <= 0:
            self._health = 0
            self.__dead()
        elif self._health > 100:
            self._health = 100

    def _update_hitbox(self) -> Tuple[int, int, int, int]:
        """Update and return the character's hitbox."""
        self.hitbox = (
            self.position_x + 17,
            self.position_on_canvas_y() + 2,
            31,
            57
        )
        return self.hitbox

    def position_on_canvas_y(self) -> int:
        """Convert game y-coordinate to screen y-coordinate."""
        return self._environment.win.get_height() - self.position_y

    def load_image(self, filename: str) -> pygame.Surface:
        """Load an image from the character's image directory."""
        path = os.path.join(self.images_path, filename)
        try:
            image = pygame.image.load(path)
            return image.convert_alpha() if image.get_alpha() else image.convert()
        except (FileNotFoundError, pygame.error) as e:
            print(f"Error loading image {filename}: {e}")
            # Return a fallback surface
            return pygame.Surface((self.width, self.high), pygame.SRCALPHA)

    def create(self) -> None:
        """Load all animation frames for the character."""
        # Right walking animation
        self.walk_right = [
            self.load_image('R1.png'), self.load_image('R2.png'),
            self.load_image('R3.png'), self.load_image('R4.png'),
            self.load_image('R5.png'), self.load_image('R6.png'),
            self.load_image('R7.png'), self.load_image('R8.png'),
            self.load_image('R9.png')
        ]

        # Left walking animation
        self.walk_left = [
            self.load_image('L1.png'), self.load_image('L2.png'),
            self.load_image('L3.png'), self.load_image('L4.png'),
            self.load_image('L5.png'), self.load_image('L6.png'),
            self.load_image('L7.png'), self.load_image('L8.png'),
            self.load_image('L9.png')
        ]

        # Standing animation
        self.standing = [self.load_image('standing.png')]

    def health_bar(self) -> None:
        """Draw the character's health bar."""
        bar_width = 50
        current_health_width = bar_width * (self.health / 100)

        pygame.draw.rect(
            self._environment.win,
            (0, 255, 0),  # Green background
            (self.hitbox[0], self.hitbox[1] - 20, bar_width, 3)
        )

        pygame.draw.rect(
            self._environment.win,
            (255, 0, 0),  # Red missing health
            (self.hitbox[0] + current_health_width, self.hitbox[1] - 20,
             bar_width - current_health_width, 3)
        )

    def draw(self) -> None:
        """Draw the character with appropriate animation frame."""
        self.health_bar()

        # Reset frame count if out of bounds
        if abs(self._frame_count) >= 27:
            self._frame_count = 0

        # Determine which animation to show
        if self.move_direction == 'left':
            self.walk_direction = 'left'
            frame_index = abs(self._frame_count // 3) % len(self.walk_left)
            self._environment.win.blit(
                self.walk_left[frame_index],
                (self.position_x, self.position_on_canvas_y())
            )
            self._frame_count -= 1

        elif self.move_direction == 'right':
            self.walk_direction = 'right'
            frame_index = abs(self._frame_count // 3) % len(self.walk_right)
            self._environment.win.blit(
                self.walk_right[frame_index],
                (self.position_x, self.position_on_canvas_y())
            )
            self._frame_count += 1

        elif self.move_direction == 'down':
            self._environment.win.blit(
                self.standing[0],
                (self.position_x, self.position_on_canvas_y())
            )

        else:  # Standing still
            self._frame_count = 0
            if self.walk_direction == 'left':
                self._environment.win.blit(
                    self.walk_left[0],
                    (self.position_x, self.position_on_canvas_y())
                )
            else:  # Default to right
                self._environment.win.blit(
                    self.walk_right[0],
                    (self.position_x, self.position_on_canvas_y())
                )

    def walk(self, x_steps: int = 1, z_steps: int = 0) -> None:
        """Move the character horizontally."""
        self.position_x += x_steps
        self.position_z += z_steps
        self._update_hitbox()

        if x_steps > 0:
            self.move_direction = 'right'
        elif x_steps < 0:
            self.move_direction = 'left'

    def jump(self, y_high: int = 5, x_steps: int = 0, surface: int = 0) -> None:
        """Make the character jump."""
        if not self.physics_state.rt.is_running:
            self.physics_state.set_setup(
                x=self.position_x,
                y=self.position_y,
                surface_x=self.position_x,
                surface_y=surface
            )

            direction_multiplier = {
                'right': 1,
                'left': -1,
                'center': 0,
                'down': 0
            }.get(self.move_direction, 0)

            self.physics_state.throw(x_steps * direction_multiplier, y_high)

    def stop(self, y_high: int = 1) -> None:
        """Stop the character's movement."""
        self.move_direction = 'down'
        self._update_hitbox()

    def attack(self) -> None:
        """Perform an attack with the character's weapon."""
        self.weapon.load(2)
        move_direction = Direction[self.move_direction]
        self.weapon.set_target(move_direction)

        # Calculate weapon position relative to character
        pos_y = self.position_y - self.high / 2
        pos_x = self.position_x + self.width * 1.5

        self.weapon.activate(pos_y, pos_x)
        self.play_sound(self.sound_hit)

    def update_position(self, prop: PhysicsObject) -> None:
        """Update position from physics simulation."""
        self.position_x = prop.x
        self.position_y = prop.y
        self._update_hitbox()

    def __dead(self) -> None:
        """Handle character death."""
        self.move_direction = 'down'
        self.physics_state.set_setup(bottom=-1500)
        self.jump(60)

    def play_sound(self, file_path: str) -> None:
        """Play a sound effect."""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(1, 0.0)
        except pygame.error as e:
            print(f"Error playing sound {file_path}: {e}")


class Goblin(Human):
    """Enemy character class derived from Human."""

    def __init__(self, environment, **attr):
        super().__init__(environment, **attr)

        # Goblin-specific properties
        self.images_path = full_file(['Resources', 'images', 'Enemy'])
        self.power = 3
        self.move_direction = 'center'
        self.walk_direction = 'left'
        self.high = 180

        # Goblin sounds
        self.sound_hooch = full_file(['Resources', 'sound', 'wound.mp3'])
        self.sound_dead = full_file(['Resources', 'sound', 'died.mp3'])

        # Attack state
        self._is_attacking = False
        self.timer = TimerController()

        # Attack animations
        self.attack_right: List[pygame.Surface] = []
        self.attack_left: List[pygame.Surface] = []

        self.create()

    def create(self) -> None:
        """Load all animation frames for the goblin."""
        # Right walking animation
        self.walk_right = [
            self.load_image('R1E.png'), self.load_image('R2E.png'),
            self.load_image('R3E.png'), self.load_image('R4E.png'),
            self.load_image('R5E.png'), self.load_image('R6E.png'),
            self.load_image('R7E.png'), self.load_image('R8E.png'),
            self.load_image('R5E.png')
        ]

        # Left walking animation
        self.walk_left = [
            self.load_image('L1E.png'), self.load_image('L2E.png'),
            self.load_image('L3E.png'), self.load_image('L4E.png'),
            self.load_image('L5E.png'), self.load_image('L6E.png'),
            self.load_image('L7E.png'), self.load_image('L8E.png'),
            self.load_image('L5E.png')
        ]

        # Standing animation
        self.standing = [self.load_image('L1E.png')]

        # Attack animations
        self.attack_right = [
            self.load_image('R9E.png'),
            self.load_image('R10E.png'),
            self.load_image('R11E.png')
        ]

        self.attack_left = [
            self.load_image('L9E.png'),
            self.load_image('L10E.png'),
            self.load_image('L11E.png')
        ]

    def draw(self) -> None:
        """Draw the goblin with appropriate animation frame."""
        if not self._is_attacking:
            super().draw()
        else:
            self._frame_count += 1
            if self.move_direction == 'left':
                frame_index = self._frame_count % 3
                self._environment.win.blit(
                    self.attack_left[frame_index],
                    (self.position_x, self.position_on_canvas_y())
                )
            else:  # Default to right
                frame_index = self._frame_count % 3
                self._environment.win.blit(
                    self.attack_right[frame_index],
                    (self.position_x, self.position_on_canvas_y())
                )

    def attack(self) -> None:
        """Initiate a goblin attack sequence."""
        self.timer.set_attr(
            timer_function=self._toggle_attack,
            start_input_args=[True],
            stop_function=self._toggle_attack,
            stop_input_args=[False],
            interval=0.1,
            limit=0.5
        )
        self.timer.start()

    def _toggle_attack(self, state: bool = True) -> None:
        """Toggle the attack animation state."""
        self._is_attacking = state