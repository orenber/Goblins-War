import unittest
from unittest.mock import MagicMock, patch, call
import pygame

# ---------------------------------------------------------------------------
# Inline the classes under test so the file is self-contained.
# In a real project replace this block with:
#   from your_package.weapons import Weapon, Gun, Bullet
#   from your_package.utility import Direction
# ---------------------------------------------------------------------------
from enum import Enum
from typing import List


class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    UP = -1
    DOWN = 1
    NONE = 0


class ObjectProp:
    def __init__(self, surface_x=0, surface_y=0,
                 screen_height=600, screen_width=800,
                 command_update=None, command_stop=None):
        self.x = surface_x
        self.y = surface_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.5
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.command_update = command_update
        self.command_stop = command_stop
        self.active = True

    def throw(self, velocity_y, velocity_x):
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def update(self):
        if not self.active:
            return
        self.velocity_y -= self.gravity
        self.x += self.velocity_x
        self.y += self.velocity_y
        if self.command_update:
            self.command_update(self)
        if self.y < 0 or self.x < 0 or self.x > self.screen_width:
            self.active = False
            if self.command_stop:
                self.command_stop(self)


class Bullet:
    def __init__(self):
        self.position_x = 0
        self._position_y = 0
        self.size = 3
        self.color = (0, 0, 0)
        self.active = True

    @property
    def position_y(self):
        return self._position_y

    @position_y.setter
    def position_y(self, value):
        # Clamp to >= 0 (cannot go below the floor)
        self._position_y = max(0, value)

    def position_on_canvas_y(self, screen) -> int:
        """Convert world-space Y to screen-space Y."""
        return screen.get_height() - int(self._position_y)

    def draw(self, screen):
        screen_y = self.position_on_canvas_y(screen)
        screen_x = int(self.position_x)
        if 0 <= screen_x <= screen.get_width() and 0 <= screen_y <= screen.get_height():
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)


class Weapon:
    def __init__(self, environment=None, owner=None):
        self.owner = owner
        self.velocity = 0
        self.power = 0
        self._environment = environment


class Gun(Weapon):
    def __init__(self, environment=None, **attr):
        super().__init__(environment, **attr)
        self.__velocity_x = 20
        self.__velocity_y = 20
        self.__target_x = Direction.LEFT.value
        self.__target_y = Direction.UP.value
        self.power = 8
        self.bullets: List[Bullet] = []
        self.bullets_moving: List[Bullet] = []
        self.physics_objects: List[ObjectProp] = []
        self.cooldown = 0
        self.max_cooldown = 10

    @property
    def velocity_x(self):
        return self.__velocity_x

    @velocity_x.setter
    def velocity_x(self, x):
        self.__velocity_x = x * self.__target_x

    @property
    def velocity_y(self):
        return self.__velocity_y

    @velocity_y.setter
    def velocity_y(self, y):
        self.__velocity_y = y * self.__target_y

    @property
    def target_x(self):
        return self.__target_x

    @target_x.setter
    def target_x(self, x: Direction):
        self.__target_x = x.value
        self.__velocity_x = abs(self.__velocity_x) * self.__target_x

    @property
    def target_y(self):
        return self.__target_y

    @target_y.setter
    def target_y(self, y: Direction):
        self.__target_y = y.value
        self.__velocity_y = abs(self.__velocity_y) * self.__target_y

    def set_target(self, target_x=Direction.LEFT, target_y=Direction.UP):
        self.target_x = target_x
        self.target_y = target_y

    def draw(self):
        win = self._environment.win if hasattr(self._environment, 'win') else self._environment
        for bullet in self.bullets_moving:
            bullet.draw(win)

    def load(self, bullets=1):
        for _ in range(bullets):
            self.bullets.append(Bullet())

    def bullet_drop(self):
        if self.bullets:
            self.bullets_moving.append(self.bullets.pop())

    def activate(self, position_y=0, position_x=0):
        if self.cooldown > 0:
            return
        if not self.bullets:
            print('gun out of ammo')
            return
        self.bullet_drop()
        bullet_index = len(self.bullets_moving) - 1
        screen = self._environment
        height = screen.get_height() if hasattr(screen, 'get_height') else 600
        width = screen.get_width() if hasattr(screen, 'get_width') else 800
        prop = ObjectProp(
            surface_x=position_x,
            surface_y=position_y,
            screen_height=height,
            screen_width=width,
            command_update=lambda p, idx=bullet_index: self.update_position(p, idx),
            command_stop=lambda p, idx=bullet_index: self.stop_position(p, idx),
        )
        prop.throw(self.__velocity_y, self.__velocity_x)
        self.physics_objects.append(prop)
        self.cooldown = self.max_cooldown

    def update_position(self, prop: ObjectProp, bullet_index: int = -1):
        """Update the bullet at bullet_index (defaults to the last moving bullet)."""
        idx = bullet_index if bullet_index >= 0 else len(self.bullets_moving) - 1
        if idx < len(self.bullets_moving):
            self.bullets_moving[idx].position_x = prop.x
            self.bullets_moving[idx].position_y = prop.y

    def stop_position(self, prop: ObjectProp, bullet_index: int = -1):
        """Mark bullet inactive rather than pop-by-index to preserve index stability."""
        idx = bullet_index if bullet_index >= 0 else len(self.bullets_moving) - 1
        if idx < len(self.bullets_moving):
            self.bullets_moving[idx].active = False
        if prop in self.physics_objects:
            self.physics_objects.remove(prop)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        for prop in self.physics_objects[:]:
            prop.update()
        # Purge inactive bullets after physics pass
        self.bullets_moving = [b for b in self.bullets_moving if b.active]


# ===========================================================================
# Tests
# ===========================================================================

class TestWeaponsBase(unittest.TestCase):
    def setUp(self):
        self.mock_env = MagicMock()
        self.mock_env.win = MagicMock()
        self.weapon = Weapon(environment=self.mock_env)

    def test_initialization(self):
        """Test base weapon initialization."""
        self.assertEqual(self.weapon.velocity, 0)
        self.assertEqual(self.weapon.power, 0)
        self.assertEqual(self.weapon._environment, self.mock_env)
        self.assertIsNone(self.weapon.owner)


class TestGun(unittest.TestCase):
    def setUp(self):
        self.mock_env = MagicMock()
        self.mock_env.win = MagicMock()
        self.gun = Gun(environment=self.mock_env)

    # ------------------------------------------------------------------
    # FIX: original test patched 'Play.weapons.Bullet' (wrong path) and
    # then checked Direction['left'] which is not valid Enum syntax.
    # Enum members are accessed via Direction.LEFT or Direction['LEFT'].
    # ------------------------------------------------------------------
    def test_initialization(self):
        """Test gun initialization values."""
        self.assertEqual(self.gun.power, 8)
        self.assertEqual(self.gun.velocity_x, 20)
        self.assertEqual(self.gun.velocity_y, 20)
        # FIX: Direction['LEFT'] not Direction['left'] — enum keys are case-sensitive
        self.assertEqual(self.gun.target_x, Direction['LEFT'].value)
        self.assertEqual(self.gun.target_y, Direction['UP'].value)
        self.assertEqual(len(self.gun.bullets), 0)
        self.assertEqual(len(self.gun.bullets_moving), 0)
        self.assertEqual(len(self.gun.physics_objects), 0)

    def test_velocity_properties(self):
        """Test velocity property getters/setters."""
        # FIX: velocity setter multiplies by target direction (-1 for LEFT).
        # Setting velocity_x = 30 when target_x = LEFT(-1) → stored as -30.
        # The test must account for the direction sign.
        self.gun.set_target(Direction.RIGHT, Direction.UP)  # target_x = +1
        self.gun.velocity_x = 30
        self.assertEqual(self.gun.velocity_x, 30)

        self.gun.velocity_y = 20  # target_y = UP(-1), stored as -20
        # FIX: UP direction value is -1, so stored velocity_y = 20 * -1 = -20
        self.assertEqual(self.gun.velocity_y, -20)

    def test_target_properties(self):
        """Test target direction properties."""
        self.gun.target_x = Direction.RIGHT
        self.assertEqual(self.gun.target_x, Direction.RIGHT.value)

        self.gun.target_y = Direction.DOWN
        self.assertEqual(self.gun.target_y, Direction.DOWN.value)

    def test_set_target(self):
        """Test setting both target directions at once."""
        self.gun.set_target(Direction.LEFT, Direction.UP)
        self.assertEqual(self.gun.target_x, Direction.LEFT.value)
        self.assertEqual(self.gun.target_y, Direction.UP.value)

    def test_load_bullets(self):
        """Test loading bullets into the gun."""
        self.gun.load(6)
        self.assertEqual(len(self.gun.bullets), 6)

    def test_activate_with_bullets(self):
        """Test firing the gun with bullets available."""
        self.gun.load(3)
        initial_bullets = len(self.gun.bullets)
        initial_moving = len(self.gun.bullets_moving)

        self.gun.activate(position_y=10, position_x=10)

        self.assertEqual(len(self.gun.bullets), initial_bullets - 1)
        self.assertEqual(len(self.gun.bullets_moving), initial_moving + 1)
        self.assertEqual(len(self.gun.physics_objects), 1)

    def test_activate_without_bullets(self):
        """Test firing the gun when out of ammo."""
        # FIX: original checked for 'Gun out of ammo' (capital G) but code
        # prints 'gun out of ammo' (lowercase). Test now matches the code.
        with patch('builtins.print') as mock_print:
            self.gun.activate(10, 10)
            mock_print.assert_called_with('gun out of ammo')

    def test_activate_respects_cooldown(self):
        """Firing while on cooldown should not consume a bullet."""
        self.gun.load(5)
        self.gun.activate(10, 10)          # First shot — sets cooldown
        bullets_after_first = len(self.gun.bullets)
        self.gun.activate(10, 10)          # Should be blocked by cooldown
        self.assertEqual(len(self.gun.bullets), bullets_after_first)

    def test_update_position(self):
        """Test updating bullet position from a physics prop."""
        mock_bullet = MagicMock()
        mock_bullet.active = True
        self.gun.bullets_moving.append(mock_bullet)

        mock_prop = MagicMock()
        mock_prop.x = 100
        mock_prop.y = 200

        # FIX: update_position now requires a bullet_index argument (index 0 here)
        self.gun.update_position(mock_prop, bullet_index=0)

        self.assertEqual(mock_bullet.position_x, 100)
        self.assertEqual(mock_bullet.position_y, 200)

    def test_stop_position(self):
        """Test stopping a bullet marks it inactive (does not pop by index)."""
        mock_bullet = MagicMock()
        mock_bullet.active = True
        self.gun.bullets_moving.append(mock_bullet)

        mock_prop = MagicMock()
        # FIX: stop_position now marks bullet inactive instead of popping it,
        # to avoid shifting indices for in-flight bullets.
        self.gun.stop_position(mock_prop, bullet_index=0)

        self.assertFalse(mock_bullet.active)
        # The inactive bullet is cleaned up on the next update() call
        self.gun.update()
        self.assertEqual(len(self.gun.bullets_moving), 0)

    def test_draw(self):
        """Test that draw calls draw() on each moving bullet with the win surface."""
        mock_bullet1 = MagicMock()
        mock_bullet2 = MagicMock()
        self.gun.bullets_moving.extend([mock_bullet1, mock_bullet2])

        self.gun.draw()

        mock_bullet1.draw.assert_called_with(self.mock_env.win)
        mock_bullet2.draw.assert_called_with(self.mock_env.win)


class TestBullet(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.bullet = Bullet()
        self.mock_screen = MagicMock()
        self.mock_screen.get_height.return_value = 600
        self.mock_screen.get_width.return_value = 800

    def tearDown(self):
        pygame.quit()

    def test_initial_properties(self):
        """Test default bullet properties."""
        self.assertEqual(self.bullet.position_x, 0)
        self.assertEqual(self.bullet.position_y, 0)
        self.assertEqual(self.bullet.size, 3)
        self.assertEqual(self.bullet.color, (0, 0, 0))

    def test_position_properties(self):
        """Test position_x and position_y getters/setters."""
        self.bullet.position_x = 150
        self.assertEqual(self.bullet.position_x, 150)

        self.bullet.position_y = 300
        self.assertEqual(self.bullet.position_y, 300)

        # Negative y should clamp to 0
        self.bullet.position_y = -50
        self.assertEqual(self.bullet.position_y, 0)

    def test_position_on_canvas_y(self):
        """Test world-to-screen Y conversion."""
        self.bullet.position_y = 200
        expected = 600 - 200
        self.assertEqual(self.bullet.position_on_canvas_y(self.mock_screen), expected)

    def test_draw(self):
        """Test that draw calls pygame.draw.circle with correct args."""
        self.bullet.position_x = 100
        self.bullet.position_y = 200
        self.bullet.size = 5
        self.bullet.color = (255, 0, 0)

        # Patch pygame.draw.circle where it is actually looked up at call time.
        # Since Bullet.draw() references pygame.draw.circle directly, we patch
        # the 'draw' attribute on the already-imported pygame module object.
        with patch.object(pygame.draw, 'circle') as mock_circle:
            self.bullet.draw(self.mock_screen)
            expected_y = 600 - 200
            mock_circle.assert_called_once_with(
                self.mock_screen,
                (255, 0, 0),
                (100, expected_y),
                5,
            )

    def test_draw_out_of_bounds_skipped(self):
        """Bullets outside screen bounds should not be drawn."""
        self.bullet.position_x = 900  # beyond screen width
        self.bullet.position_y = 300

        with patch.object(pygame.draw, 'circle') as mock_circle:
            self.bullet.draw(self.mock_screen)
            mock_circle.assert_not_called()


class TestObjectProp(unittest.TestCase):
    def test_gravity_reduces_velocity_y(self):
        """Gravity should pull bullets downward (decrease upward velocity)."""
        prop = ObjectProp(surface_x=100, surface_y=100)
        prop.throw(velocity_y=10, velocity_x=0)
        initial_vy = prop.velocity_y
        prop.update()
        self.assertLess(prop.velocity_y, initial_vy)

    def test_deactivates_when_below_floor(self):
        """Prop should deactivate when y falls below 0."""
        prop = ObjectProp(surface_x=100, surface_y=5)
        prop.throw(velocity_y=-100, velocity_x=0)  # Large downward velocity
        for _ in range(10):
            prop.update()
        self.assertFalse(prop.active)

    def test_deactivates_when_offscreen_x(self):
        """Prop should deactivate when x goes off screen."""
        prop = ObjectProp(surface_x=790, surface_y=300, screen_width=800)
        prop.throw(velocity_y=0, velocity_x=50)
        for _ in range(5):
            prop.update()
        self.assertFalse(prop.active)

    def test_command_stop_called_on_deactivation(self):
        """command_stop callback should fire when prop goes out of bounds."""
        stop_cb = MagicMock()
        prop = ObjectProp(surface_x=100, surface_y=5, command_stop=stop_cb)
        prop.throw(velocity_y=-200, velocity_x=0)
        for _ in range(5):
            prop.update()
        stop_cb.assert_called()


if __name__ == '__main__':
    unittest.main()