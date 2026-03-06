import pygame
import os
from typing import List, Tuple
from Play.physics import PhysicsObject
from Play.weapons import Gun
from Utility import Direction, full_file
from Utility.timer_utility import TimerController


class Human:
    def __init__(self, environment, **attr):
        self._environment = environment
        self._frame_count = 0
        self._size_factor = 1 / 3
        self._is_jump = False
        self._health = 100
        self._live = True
        self.power = 20
        self.high = 180
        self.width = 60
        self.position_x = 200
        self._position_y = 0
        self.position_z = 0
        self.jump_count = 10
        self.move_direction = 'center'
        self.walk_direction = 'right'
        self.physics_state = PhysicsObject()
        self.physics_state.on_update = lambda prop: self.update_position(prop)
        self.weapon = Gun(environment)
        self.images_path = full_file(['Resources', 'images', 'Hero'])
        self.sound_hit = full_file(['Resources', 'sound', 'hit.mp3'])
        self.walk_right: List[pygame.Surface] = []
        self.walk_left: List[pygame.Surface] = []
        self.standing: List[pygame.Surface] = []
        self.hitbox = self._update_hitbox()
        self.set_setup(**attr)
        self.create()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def _win(self) -> pygame.Surface:
        """Return the pygame Surface regardless of whether _environment is a
        Nature wrapper or a bare Surface. Centralises the resolution so every
        draw / hitbox call uses the same safe accessor."""
        env = self._environment
        return env.win if hasattr(env, 'win') else env

    def set_setup(self, **prop) -> None:
        valid = {'position_x', 'position_y', 'high', 'width', 'walk_direction'}
        unknown = set(prop.keys()) - valid
        if unknown:
            raise ValueError(f'Unknown attributes: {unknown}')
        for name, value in prop.items():
            setattr(self, name, value)

    @property
    def live(self) -> bool:
        self._live = self.health > 0
        return self._live

    @property
    def high(self) -> int:
        return int(self._high * self._size_factor)

    @high.setter
    def high(self, value: int) -> None:
        self._high = value

    @property
    def width(self) -> int:
        return int(self._width * self._size_factor)

    @width.setter
    def width(self, value: int) -> None:
        self._width = value

    @property
    def position_y(self) -> int:
        return self._position_y

    @position_y.setter
    def position_y(self, value: int) -> None:
        if value < 0 and self.health > 0:
            value = 0
        self._position_y = value
        self._update_hitbox()

    @property
    def health(self) -> int:
        return self._health

    @health.setter
    def health(self, value: int) -> None:
        self._health = max(0, min(100, value))
        if self._health == 0:
            self.__dead()

    def _update_hitbox(self) -> Tuple[int, int, int, int]:
        self.hitbox = (
            self.position_x + 17,
            self.position_on_canvas_y() + 2,
            31, 57
        )
        return self.hitbox

    def position_on_canvas_y(self) -> int:
        # FIX 2: _environment may be a Nature wrapper (which stores the pygame
        # Surface as .win) or a bare pygame Surface. Resolve to the actual
        # Surface before calling get_height() so neither Gun.activate() nor
        # any coordinate helper crashes with "AttributeError: 'Nature' object
        # has no attribute 'get_height'".
        return self._win.get_height() - self._position_y - self.high

    def load_image(self, filename: str) -> pygame.Surface:
        path = os.path.join(self.images_path, filename)
        try:
            image = pygame.image.load(path)
            return image.convert_alpha() if image.get_alpha() else image.convert()
        except (FileNotFoundError, pygame.error) as e:
            print(f"Error loading image {filename}: {e}")
            return pygame.Surface((self.width, self.high), pygame.SRCALPHA)

    def create(self) -> None:
        self.walk_right = [self.load_image(f'R{i}.png') for i in range(1, 10)]
        self.walk_left  = [self.load_image(f'L{i}.png') for i in range(1, 10)]
        self.standing   = [self.load_image('standing.png')]

    def health_bar(self) -> None:
        bar_width = 50
        current_health_width = bar_width * (self.health / 100)
        hx, hy = self.hitbox[0], self.hitbox[1]
        pygame.draw.rect(self._win, (0, 255, 0),
                         (hx, hy - 20, current_health_width, 3))
        pygame.draw.rect(self._win, (255, 0, 0),
                         (hx + current_health_width, hy - 20,
                          bar_width - current_health_width, 3))

    def draw(self) -> None:
        self.health_bar()
        anim_len = 27
        if abs(self._frame_count) >= anim_len:
            self._frame_count = 0
        draw_x = self.position_x
        draw_y = self.position_on_canvas_y()
        if self.move_direction == 'left':
            self.walk_direction = 'left'
            frame_index = abs(self._frame_count // 3) % len(self.walk_left)
            self._win.blit(self.walk_left[frame_index], (draw_x, draw_y))
            self._frame_count -= 1
        elif self.move_direction == 'right':
            self.walk_direction = 'right'
            frame_index = abs(self._frame_count // 3) % len(self.walk_right)
            self._win.blit(self.walk_right[frame_index], (draw_x, draw_y))
            self._frame_count += 1
        elif self.move_direction == 'down':
            self._win.blit(self.standing[0], (draw_x, draw_y))
        else:
            self._frame_count = 0
            frames = self.walk_left if self.walk_direction == 'left' else self.walk_right
            self._win.blit(frames[0], (draw_x, draw_y))

    def walk(self, x_steps: int = 1, z_steps: int = 0) -> None:
        self.position_x += x_steps
        self.position_z += z_steps
        self._update_hitbox()
        if x_steps > 0:
            self.move_direction = 'right'
        elif x_steps < 0:
            self.move_direction = 'left'

    def jump(self, y_high: int = 5, x_steps: int = 0, surface: int = 0) -> None:
        if not self.physics_state.is_moving:
            self.physics_state.set_setup(
                x=self.position_x, y=self.position_y,
                surface_x=self.position_x, surface_y=surface
            )
            direction_multiplier = {
                'right': 1, 'left': -1, 'center': 0, 'down': 0,
            }.get(self.move_direction, 0)
            self.physics_state.throw(x_steps * direction_multiplier, y_high)

    def stop(self) -> None:
        self.move_direction = 'down'
        self._update_hitbox()

    def attack(self) -> None:
        self.weapon.load(2)
        direction_key = self.walk_direction
        move_direction = Direction[direction_key.upper()]
        self.weapon.set_target(move_direction)
        pos_y = self.position_y - self.high / 2
        pos_x = self.position_x + self.width * 1.5
        self.weapon.activate(pos_y, pos_x)
        self.play_sound(self.sound_hit)

    def update_position(self, prop) -> None:
        self.position_x = prop.x
        self.position_y = prop.y
        self._update_hitbox()

    def __dead(self) -> None:
        self.move_direction = 'down'
        self.physics_state.set_setup(bottom=-1500)
        self.jump(60)

    def play_sound(self, file_path: str) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound = pygame.mixer.Sound(file_path)
            sound.play()
        except pygame.error as e:
            print(f"Error playing sound {file_path}: {e}")


class Goblin(Human):
    """Enemy character derived from Human."""

    def __init__(self, environment, **attr):
        # FIX 1: super().__init__() ends by calling self.create(), which Python
        # dispatches to Goblin.create() even during the super() call. At that
        # point self.images_path still points at the Hero folder, so every
        # Goblin-specific image (R9E–R11E, L9E–L11E) is looked up in the wrong
        # directory and fails. Set images_path to the Enemy folder first so the
        # create() call inside super() already uses the correct path.
        self.images_path = os.path.join(
            os.path.dirname(full_file(['Resources', 'images', 'Enemy'])),
            'Enemy'
        )

        super().__init__(environment, **attr)

        # Re-set via full_file for the canonical absolute path
        self.images_path = full_file(['Resources', 'images', 'Enemy'])
        self.power = 3
        self.move_direction = 'center'
        self.walk_direction = 'left'
        self.high = 180
        self.sound_hooch = full_file(['Resources', 'sound', 'wound.mp3'])
        self.sound_dead  = full_file(['Resources', 'sound', 'died.mp3'])
        self._is_attacking = False
        self.timer = TimerController()
        self.attack_right: List[pygame.Surface] = []
        self.attack_left:  List[pygame.Surface] = []
        self.create()

    def create(self) -> None:
        self.walk_right = [self.load_image(f'R{i}E.png') for i in range(1, 9)] + \
                          [self.load_image('R5E.png')]
        self.walk_left  = [self.load_image(f'L{i}E.png') for i in range(1, 9)] + \
                          [self.load_image('L5E.png')]
        self.standing   = [self.load_image('L1E.png')]
        self.attack_right = [self.load_image(f'R{i}E.png') for i in range(9, 12)]
        self.attack_left  = [self.load_image(f'L{i}E.png') for i in range(9, 12)]

    def draw(self) -> None:
        if not self._is_attacking:
            super().draw()
            return
        self._frame_count += 1
        frame_index = self._frame_count % len(self.attack_left)
        draw_x = self.position_x
        draw_y = self.position_on_canvas_y()
        frames = self.attack_left if self.move_direction == 'left' else self.attack_right
        self._win.blit(frames[frame_index], (draw_x, draw_y))

    def attack(self) -> None:
        self._frame_count = 0
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
        self._is_attacking = state
        if not state:
            self._frame_count = 0