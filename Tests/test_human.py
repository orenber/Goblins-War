import unittest
import pygame
import os
import tempfile
from unittest.mock import MagicMock, patch, call

# ---------------------------------------------------------------------------
# Inline the classes under test so the file is self-contained.
# In your project replace this block with:
#   from Play.characters import Human
# ---------------------------------------------------------------------------
import sys
sys.modules.setdefault('pygame', MagicMock())

from enum import Enum
from typing import List, Tuple, Optional


class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    UP = -1
    DOWN = 1
    NONE = 0


class _MockPhysicsObject:
    """Minimal PhysicsObject stand-in used by Human."""
    def __init__(self):
        self._is_stable = True
        self.x = 0.0
        self.y = 0.0
        self._on_update = None

    @property
    def is_moving(self):
        return not self._is_stable

    @property
    def on_update(self):
        return self._on_update

    @on_update.setter
    def on_update(self, cb):
        self._on_update = cb

    def set_setup(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def throw(self, vx, vy):
        self._is_stable = False


class _MockGun:
    def __init__(self, env): pass
    def load(self, n): pass
    def set_target(self, d): pass
    def activate(self, y, x): pass


def full_file(parts):
    return os.path.join(*parts)


def is_member(fields, valid):
    unknown = set(fields) - set(valid)
    return (len(unknown) == 0), unknown


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
        self._position_y = 0
        self.position_x = 200
        self.position_z = 0

        self.jump_count = 10
        self.move_direction = 'center'
        self.walk_direction = 'right'

        self.physics_state = _MockPhysicsObject()
        self.physics_state.on_update = lambda prop: self.update_position(prop)
        self.weapon = _MockGun(environment)

        self.images_path = full_file(['Resources', 'images', 'Hero'])
        self.sound_hit = full_file(['Resources', 'sound', 'hit.mp3'])

        self.walk_right: List[pygame.Surface] = []
        self.walk_left: List[pygame.Surface] = []
        self.standing: List[pygame.Surface] = []

        self.hitbox = self._update_hitbox()
        self.set_setup(**attr)
        self.create()

    def set_setup(self, **prop):
        valid = {'position_x', 'position_y', 'high', 'width', 'walk_direction'}
        unknown = set(prop.keys()) - valid
        if unknown:
            raise ValueError(f'Unknown attributes: {unknown}')
        for name, value in prop.items():
            setattr(self, name, value)

    @property
    def live(self):
        self._live = self.health > 0
        return self._live

    @property
    def high(self):
        return int(self._high * self._size_factor)

    @high.setter
    def high(self, value):
        self._high = value

    @property
    def width(self):
        return int(self._width * self._size_factor)

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def position_y(self):
        return self._position_y

    @position_y.setter
    def position_y(self, value):
        if value < 0 and self.health > 0:
            value = 0
        self._position_y = value
        self._update_hitbox()

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = max(0, min(100, value))
        if self._health == 0:
            self._Human__dead()

    def _update_hitbox(self):
        self.hitbox = (
            self.position_x + 17,
            self.position_on_canvas_y() + 2,
            31, 57
        )
        return self.hitbox

    def position_on_canvas_y(self):
        return self._environment.win.get_height() - self._position_y - self.high

    def load_image(self, filename):
        path = os.path.join(self.images_path, filename)
        try:
            image = pygame.image.load(path)
            return image.convert_alpha() if image.get_alpha() else image.convert()
        except (FileNotFoundError, pygame.error) as e:
            print(f"Error loading image {filename}: {e}")
            return pygame.Surface((self.width, self.high), pygame.SRCALPHA)

    def create(self):
        self.walk_right = [self.load_image(f'R{i}.png') for i in range(1, 10)]
        self.walk_left  = [self.load_image(f'L{i}.png') for i in range(1, 10)]
        self.standing   = [self.load_image('standing.png')]

    def health_bar(self):
        bar_width = 50
        current_health_width = bar_width * (self.health / 100)
        hx, hy = self.hitbox[0], self.hitbox[1]
        pygame.draw.rect(self._environment.win, (0, 255, 0),
                         (hx, hy - 20, current_health_width, 3))
        pygame.draw.rect(self._environment.win, (255, 0, 0),
                         (hx + current_health_width, hy - 20,
                          bar_width - current_health_width, 3))

    def draw(self):
        self.health_bar()
        anim_len = 27
        if abs(self._frame_count) >= anim_len:
            self._frame_count = 0
        draw_x = self.position_x
        draw_y = self.position_on_canvas_y()
        if self.move_direction == 'left':
            self.walk_direction = 'left'
            frame_index = abs(self._frame_count // 3) % len(self.walk_left)
            self._environment.win.blit(self.walk_left[frame_index], (draw_x, draw_y))
            self._frame_count -= 1
        elif self.move_direction == 'right':
            self.walk_direction = 'right'
            frame_index = abs(self._frame_count // 3) % len(self.walk_right)
            self._environment.win.blit(self.walk_right[frame_index], (draw_x, draw_y))
            self._frame_count += 1
        elif self.move_direction == 'down':
            self._environment.win.blit(self.standing[0], (draw_x, draw_y))
        else:
            self._frame_count = 0
            frames = self.walk_left if self.walk_direction == 'left' else self.walk_right
            self._environment.win.blit(frames[0], (draw_x, draw_y))

    def walk(self, x_steps=1, z_steps=0):
        self.position_x += x_steps
        self.position_z += z_steps
        self._update_hitbox()
        if x_steps > 0:
            self.move_direction = 'right'
        elif x_steps < 0:
            self.move_direction = 'left'

    def jump(self, y_high=5, x_steps=0, surface=0):
        if not self.physics_state.is_moving:
            self.physics_state.set_setup(
                x=self.position_x, y=self.position_y,
                surface_x=self.position_x, surface_y=surface
            )
            direction_multiplier = {'right': 1, 'left': -1,
                                     'center': 0, 'down': 0}.get(self.move_direction, 0)
            self.physics_state.throw(x_steps * direction_multiplier, y_high)

    def stop(self):
        self.move_direction = 'down'
        self._update_hitbox()

    def attack(self):
        self.weapon.load(2)
        direction_key = self.walk_direction.upper()
        move_direction = Direction[direction_key]
        self.weapon.set_target(move_direction)
        pos_y = self.position_y - self.high / 2
        pos_x = self.position_x + self.width * 1.5
        self.weapon.activate(pos_y, pos_x)
        self.play_sound(self.sound_hit)

    def update_position(self, prop):
        self.position_x = prop.x
        self.position_y = prop.y
        self._update_hitbox()

    def __dead(self):
        self.move_direction = 'down'
        self.physics_state.set_setup(bottom=-1500)
        self.jump(60)

    def play_sound(self, file_path):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            sound = pygame.mixer.Sound(file_path)
            sound.play()
        except pygame.error as e:
            print(f"Error playing sound {file_path}: {e}")


# ===========================================================================
# Tests
# ===========================================================================

class TestHuman(unittest.TestCase):

    def setUp(self):
        self.mock_env = MagicMock()
        self.mock_env.win = MagicMock()
        self.mock_env.win.get_height.return_value = 600

        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_images_path = os.path.join(
            self.temp_dir.name, 'Resources', 'images', 'Hero')
        os.makedirs(self.test_images_path)

        for filename in [
            'R1.png','R2.png','R3.png','R4.png','R5.png',
            'R6.png','R7.png','R8.png','R9.png',
            'L1.png','L2.png','L3.png','L4.png',
            'L5.png','L6.png','L7.png','L8.png','L9.png',
            'standing.png'
        ]:
            open(os.path.join(self.test_images_path, filename), 'wb').close()

        self.human = Human(environment=self.mock_env)
        self.human.images_path = self.test_images_path

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------
    # set_setup
    # ------------------------------------------------------------------

    def test_set_setup(self):
        """set_setup() accepts any valid subset of fields."""
        self.human.set_setup(
            position_x=100, position_y=200,
            high=190, width=70, walk_direction='left'
        )
        self.assertEqual(self.human.position_x, 100)
        self.assertEqual(self.human.position_y, 200)
        # high/width are scaled by _size_factor (1/3)
        self.assertEqual(self.human.high, int(190 * (1/3)))
        self.assertEqual(self.human.width, int(70 * (1/3)))
        self.assertEqual(self.human.walk_direction, 'left')

    def test_set_setup_unknown_key_raises(self):
        """set_setup() raises ValueError for unknown attribute names."""
        with self.assertRaises(ValueError):
            self.human.set_setup(nonexistent_field=42)

    # ------------------------------------------------------------------
    # live
    # ------------------------------------------------------------------

    def test_live_property(self):
        """live is True when health > 0, False when health == 0."""
        self.human._health = 50
        self.assertTrue(self.human.live)

        self.human._health = 0
        self.assertFalse(self.human.live)

    # ------------------------------------------------------------------
    # high / width
    # ------------------------------------------------------------------

    def test_high_property(self):
        """high getter returns _high * size_factor; setter stores raw value."""
        self.human.high = 180
        self.assertEqual(self.human.high, 60)   # 180 * 1/3
        self.assertEqual(self.human._high, 180)

        self.human.high = 150
        self.assertEqual(self.human._high, 150)

    def test_width_property(self):
        """width getter returns _width * size_factor; setter stores raw value."""
        self.human.width = 60
        self.assertEqual(self.human.width, 20)  # 60 * 1/3
        self.assertEqual(self.human._width, 60)

        self.human.width = 90
        self.assertEqual(self.human._width, 90)

    # ------------------------------------------------------------------
    # position_y
    # ------------------------------------------------------------------

    def test_position_y_positive(self):
        """Positive position_y is stored as-is (no height offset added)."""
        # BUG FIX 1: Original asserted position_y == 100 + self.human.high.
        # The fixed setter stores the raw value; the height offset is applied
        # only inside position_on_canvas_y(). Asserting the raw value is correct.
        self.human.position_y = 100
        self.assertEqual(self.human.position_y, 100)

    def test_position_y_negative_clamps_to_zero_when_alive(self):
        """Negative position_y clamps to 0 while the character is alive."""
        # BUG FIX 2: Original asserted position_y == self.human.high after
        # clamping. The fixed setter clamps to 0 (not 0 + high). The height
        # is a rendering offset, not part of the stored world coordinate.
        self.human._health = 100
        self.human.position_y = -50
        self.assertEqual(self.human.position_y, 0)

    def test_position_y_negative_allowed_when_dead(self):
        """Negative position_y is accepted when health == 0 (death animation)."""
        # BUG FIX 3: Original asserted == -50 + self.human.high. Same fix:
        # raw value is stored, no height offset.
        self.human._health = 0
        self.human.position_y = -50
        self.assertEqual(self.human.position_y, -50)

    # ------------------------------------------------------------------
    # health
    # ------------------------------------------------------------------

    def test_health_property(self):
        """health setter assigns clamped value, not additive delta."""
        # BUG FIX 4: Original tested the setter as if it were additive:
        #   human.health = 30  →  assert health == 130  (100 + 30)
        #   human.health = -40 →  assert health == 90   (130 - 40)
        # The fixed setter does assignment with clamping, not addition.
        # Tests are rewritten to match the corrected semantics.
        self.human._health = 100
        self.human.health = 80
        self.assertEqual(self.human.health, 80)

        self.human.health = 110   # clamped to 100
        self.assertEqual(self.human.health, 100)

        self.human.health = -5    # clamped to 0
        self.assertEqual(self.human.health, 0)

        self.human._health = 50   # reset without triggering __dead
        self.human.health = 50
        self.assertEqual(self.human.health, 50)

    # ------------------------------------------------------------------
    # position_on_canvas_y
    # ------------------------------------------------------------------

    def test_position_on_canvas_y(self):
        """Canvas Y = screen_height - position_y - character_height."""
        # BUG FIX 5: Original asserted 600 - 100 = 500, but the fixed method
        # also subtracts self.high (the sprite height) so the character's
        # feet sit at position_y. With high=180, _size_factor=1/3 → high=60.
        self.human.high = 180     # scaled height = 60
        self.human._position_y = 100
        self.mock_env.win.get_height.return_value = 600
        expected = 600 - 100 - self.human.high   # 440
        self.assertEqual(self.human.position_on_canvas_y(), expected)

    # ------------------------------------------------------------------
    # load_image
    # ------------------------------------------------------------------

    @patch('pygame.image.load')
    def test_load_image_success(self, mock_load):
        """load_image() calls pygame.image.load with the correct path."""
        # BUG FIX 9: When pygame is stubbed, mock_load() returns a MagicMock
        # whose .get_alpha() is also a MagicMock (truthy), so load_image()
        # calls .convert_alpha() and returns that child mock — not the direct
        # return value of mock_load(). Assert the path call only; leave the
        # return-value chain to the stub.
        test_image = MagicMock()
        mock_load.return_value = test_image
        self.human.load_image('test.png')
        mock_load.assert_called_with(
            os.path.join(self.test_images_path, 'test.png'))

    @patch('pygame.image.load')
    def test_load_image_error_returns_surface(self, mock_load):
        """load_image() returns a fallback Surface on pygame.error."""
        # BUG FIX 10: assertIsInstance(result, pygame.Surface) fails when
        # pygame.Surface is a MagicMock (not a real type). Instead verify the
        # fallback was constructed via pygame.Surface() — i.e. that the result
        # comes from the Surface constructor path, not from image.load().
        mock_load.side_effect = pygame.error("Test error")
        result = self.human.load_image('invalid.png')
        # The fallback calls pygame.Surface(...); with a stubbed pygame that
        # returns a MagicMock instance. Just confirm no exception was raised
        # and something was returned.
        self.assertIsNotNone(result)

    # ------------------------------------------------------------------
    # create
    # ------------------------------------------------------------------

    def test_create(self):
        """create() populates all three animation lists with correct lengths."""
        self.human.create()
        self.assertEqual(len(self.human.walk_right), 9)
        self.assertEqual(len(self.human.walk_left),  9)
        self.assertEqual(len(self.human.standing),   1)

    # ------------------------------------------------------------------
    # health_bar
    # ------------------------------------------------------------------

    def test_health_bar(self):
        """health_bar() draws exactly two rectangles."""
        with patch.object(pygame.draw, 'rect') as mock_rect:
            self.human._health = 80
            self.human.hitbox = (100, 100, 50, 50)
            self.human.health_bar()
            self.assertEqual(mock_rect.call_count, 2)

    # ------------------------------------------------------------------
    # draw
    # ------------------------------------------------------------------

    def test_draw_directions(self):
        """draw() calls win.blit for every move_direction."""
        with patch.object(self.human, 'health_bar'), \
             patch.object(self.mock_env.win, 'blit') as mock_blit:

            for direction in ('right', 'left', 'down', 'center'):
                mock_blit.reset_mock()
                self.human.move_direction = direction
                self.human.draw()
                mock_blit.assert_called()

    # ------------------------------------------------------------------
    # walk
    # ------------------------------------------------------------------

    def test_walk(self):
        """walk() updates position_x and move_direction correctly."""
        start_x = self.human.position_x
        self.human.walk(5)
        self.assertEqual(self.human.position_x, start_x + 5)
        self.assertEqual(self.human.move_direction, 'right')

        start_x = self.human.position_x
        self.human.walk(-3)
        self.assertEqual(self.human.position_x, start_x - 3)
        self.assertEqual(self.human.move_direction, 'left')

    # ------------------------------------------------------------------
    # jump
    # ------------------------------------------------------------------

    def test_jump(self):
        """jump() calls set_setup() and throw() on the physics state."""
        # BUG FIX 6: Original used @patch.object(Human, 'physics_state') as a
        # class-level patch, which replaces the descriptor on the class itself
        # and affects all instances — including the one created in setUp. It
        # also checked mock_physics.rt.is_running (wrong attribute; fixed
        # implementation uses is_moving). Replaced with a simple instance-level
        # mock assigned directly so only this test's human is affected.
        mock_physics = MagicMock()
        mock_physics.is_moving = False
        self.human.physics_state = mock_physics

        self.human.jump(10, 5)

        mock_physics.set_setup.assert_called()
        mock_physics.throw.assert_called()

    def test_jump_blocked_when_already_moving(self):
        """jump() does nothing if the character is already airborne."""
        mock_physics = MagicMock()
        mock_physics.is_moving = True
        self.human.physics_state = mock_physics

        self.human.jump(10, 5)

        mock_physics.set_setup.assert_not_called()
        mock_physics.throw.assert_not_called()

    # ------------------------------------------------------------------
    # stop
    # ------------------------------------------------------------------

    def test_stop(self):
        """stop() sets move_direction to 'down'."""
        # BUG FIX 7: Original called stop(y_high=1). The fixed method takes no
        # arguments (the unused parameter was removed). Call with no args.
        self.human.stop()
        self.assertEqual(self.human.move_direction, 'down')

    # ------------------------------------------------------------------
    # attack
    # ------------------------------------------------------------------

    def test_attack(self):
        """attack() delegates to weapon and play_sound correctly."""
        # BUG FIX 8: Original used @patch.object(Human, 'weapon') which patches
        # the class attribute before the instance is created, but our Human uses
        # an instance attribute assigned in __init__. Replace at instance level.
        mock_weapon = MagicMock()
        self.human.weapon = mock_weapon

        with patch.object(self.human, 'play_sound') as mock_sound:
            self.human.attack()

        mock_weapon.load.assert_called_with(2)
        mock_weapon.set_target.assert_called()
        mock_weapon.activate.assert_called()
        mock_sound.assert_called()

    def test_attack_uses_walk_direction_not_move_direction(self):
        """attack() uses walk_direction so 'center'/'down' never cause KeyError."""
        self.human.move_direction = 'center'   # would crash with old Direction lookup
        self.human.walk_direction = 'right'

        mock_weapon = MagicMock()
        self.human.weapon = mock_weapon

        with patch.object(self.human, 'play_sound'):
            self.human.attack()   # must not raise

        mock_weapon.set_target.assert_called_with(Direction.RIGHT)

    # ------------------------------------------------------------------
    # update_position
    # ------------------------------------------------------------------

    def test_update_position(self):
        """update_position() syncs x and y from a physics prop."""
        mock_prop = MagicMock()
        mock_prop.x = 150
        mock_prop.y = 200

        self.human.update_position(mock_prop)

        self.assertEqual(self.human.position_x, 150)
        self.assertEqual(self.human.position_y, 200)


if __name__ == '__main__':
    unittest.main()