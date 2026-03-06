import unittest
from unittest.mock import MagicMock, patch, call
import sys

# ---------------------------------------------------------------------------
# Stub pygame before anything imports it so the test is runnable without a
# display. In your project replace the inline class block below with:
#   from Play.weapons import Gun, Bullet
#   from Utility import Direction
# ---------------------------------------------------------------------------
sys.modules.setdefault('pygame', MagicMock())

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
        self._position_y = max(0, value)

    def draw(self, screen):
        import pygame
        screen_y = screen.get_height() - int(self._position_y)
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
        width  = screen.get_width()  if hasattr(screen, 'get_width')  else 800
        prop = ObjectProp(
            surface_x=position_x,
            surface_y=position_y,
            screen_height=height,
            screen_width=width,
            command_update=lambda p, idx=bullet_index: self.update_position(p, idx),
            command_stop= lambda p, idx=bullet_index: self.stop_position(p, idx),
        )
        prop.throw(self.__velocity_y, self.__velocity_x)
        self.physics_objects.append(prop)
        self.cooldown = self.max_cooldown

    def update_position(self, prop, bullet_index=-1):
        idx = bullet_index if bullet_index >= 0 else len(self.bullets_moving) - 1
        if idx < len(self.bullets_moving):
            self.bullets_moving[idx].position_x = prop.x
            self.bullets_moving[idx].position_y = prop.y

    def stop_position(self, prop, bullet_index=-1):
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
        self.bullets_moving = [b for b in self.bullets_moving if b.active]


# ===========================================================================
# Tests
# ===========================================================================

class TestGun(unittest.TestCase):

    def setUp(self):
        self.mock_env = MagicMock()
        self.mock_env.win = MagicMock()
        # Gun.activate() calls get_height/get_width on the environment directly
        self.mock_env.get_height.return_value = 600
        self.mock_env.get_width.return_value = 800
        self.gun = Gun(environment=self.mock_env)

    # ------------------------------------------------------------------
    # load
    # ------------------------------------------------------------------

    def test_load(self):
        """Loading N bullets appends N Bullet instances to gun.bullets."""
        self.gun.load(6)
        self.assertEqual(len(self.gun.bullets), 6)
        # Every item must be a Bullet
        self.assertTrue(all(isinstance(b, Bullet) for b in self.gun.bullets))

    # ------------------------------------------------------------------
    # activate
    # ------------------------------------------------------------------

    def test_activate_with_bullets(self):
        """Firing moves one bullet from the reserve to bullets_moving."""
        self.gun.load(3)
        initial_bullets = len(self.gun.bullets)
        initial_moving  = len(self.gun.bullets_moving)

        self.gun.activate(position_y=10, position_x=10)

        self.assertEqual(len(self.gun.bullets),        initial_bullets - 1)
        self.assertEqual(len(self.gun.bullets_moving), initial_moving  + 1)
        self.assertEqual(len(self.gun.physics_objects), 1)

    def test_activate_without_bullets(self):
        """Firing with no ammo prints the out-of-ammo message."""
        # BUG FIX 1: Original patched 'Play.weapons.Bullet' — wrong module path.
        # The out-of-ammo branch only calls print(); no Bullet patch is needed.
        with patch('builtins.print') as mock_print:
            self.gun.activate(10, 10)
            mock_print.assert_called_with('gun out of ammo')

    def test_activate_respects_cooldown(self):
        """A second shot while on cooldown does not consume a bullet."""
        self.gun.load(5)
        self.gun.activate(10, 10)
        reserve_after_first = len(self.gun.bullets)
        self.gun.activate(10, 10)           # blocked by cooldown
        self.assertEqual(len(self.gun.bullets), reserve_after_first)

    # ------------------------------------------------------------------
    # update_position / stop_position
    # ------------------------------------------------------------------

    def test_update_position(self):
        """update_position() writes prop x/y to the correct bullet."""
        # BUG FIX 2: Original called update_position(prop) with no bullet_index.
        # The fixed implementation requires an index to avoid the closure-capture
        # bug. Pass bullet_index=0 to match the first (and only) moving bullet.
        mock_bullet = MagicMock()
        mock_bullet.active = True
        self.gun.bullets_moving.append(mock_bullet)

        mock_prop = MagicMock()
        mock_prop.x = 100
        mock_prop.y = 200

        self.gun.update_position(mock_prop, bullet_index=0)

        self.assertEqual(mock_bullet.position_x, 100)
        self.assertEqual(mock_bullet.position_y, 200)

    def test_stop_position(self):
        """stop_position() marks the bullet inactive; update() purges it."""
        # BUG FIX 3: Original expected immediate removal from bullets_moving
        # (len == 0 right after stop_position). The fixed implementation marks
        # inactive and purges on the next update() to preserve index stability.
        mock_bullet = MagicMock()
        mock_bullet.active = True
        self.gun.bullets_moving.append(mock_bullet)

        mock_prop = MagicMock()
        self.gun.stop_position(mock_prop, bullet_index=0)

        # Bullet is marked inactive but not yet removed
        self.assertFalse(mock_bullet.active)

        # After update() the inactive bullet is purged
        self.gun.update()
        self.assertEqual(len(self.gun.bullets_moving), 0)

    # ------------------------------------------------------------------
    # draw
    # ------------------------------------------------------------------

    def test_draw(self):
        """draw() calls bullet.draw(env.win) for every moving bullet."""
        mock_bullet1 = MagicMock()
        mock_bullet2 = MagicMock()
        self.gun.bullets_moving.extend([mock_bullet1, mock_bullet2])

        self.gun.draw()

        mock_bullet1.draw.assert_called_with(self.mock_env.win)
        mock_bullet2.draw.assert_called_with(self.mock_env.win)

    # ------------------------------------------------------------------
    # velocity properties
    # ------------------------------------------------------------------

    def test_velocity_properties(self):
        """velocity_x and velocity_y getters/setters account for direction sign."""
        # BUG FIX 4: Original tested:
        #   gun.velocity_x = 30  →  assertEqual(gun.velocity_x, 30)
        #   gun.velocity_y = 20  →  assertEqual(gun.velocity_y, 20)
        # The setter multiplies the value by the current direction sign, so the
        # stored value depends on target_x / target_y.
        #
        # With target_x=RIGHT(+1): velocity_x = 30 * 1  =  30  ✓
        # With target_y=UP(-1):    velocity_y = 20 * -1 = -20  ✗ (original asserted 20)
        #
        # Fix: set RIGHT/UP explicitly, then assert the direction-adjusted values.
        self.gun.set_target(Direction.RIGHT, Direction.UP)

        self.gun.velocity_x = 30
        self.assertEqual(self.gun.velocity_x, 30)    # RIGHT(+1): 30 * 1 = 30

        self.gun.velocity_y = 20
        self.assertEqual(self.gun.velocity_y, -20)   # UP(-1):    20 * -1 = -20

    def test_velocity_properties_left_down(self):
        """velocity sign flips correctly when direction is LEFT / DOWN."""
        self.gun.set_target(Direction.LEFT, Direction.DOWN)

        self.gun.velocity_x = 15
        self.assertEqual(self.gun.velocity_x, -15)   # LEFT(-1)

        self.gun.velocity_y = 10
        self.assertEqual(self.gun.velocity_y, 10)    # DOWN(+1)

    # ------------------------------------------------------------------
    # target properties
    # ------------------------------------------------------------------

    def test_target_properties(self):
        """target_x and target_y setters accept Direction enum members."""
        # BUG FIX 5: Original used Direction['right'] / Direction['down'].
        # Enum member lookup by name is Direction['RIGHT'] (case-sensitive).
        # Direction['right'] raises KeyError. Use attribute access instead,
        # which is unambiguous and consistent with the rest of the codebase.
        self.gun.target_x = Direction.RIGHT
        self.assertEqual(self.gun.target_x, Direction.RIGHT.value)

        self.gun.target_y = Direction.DOWN
        self.assertEqual(self.gun.target_y, Direction.DOWN.value)

    def test_set_target(self):
        """set_target() updates both axes atomically."""
        # BUG FIX 6: Same Direction['left'] / Direction['up'] KeyError as above.
        self.gun.set_target(Direction.LEFT, Direction.UP)
        self.assertEqual(self.gun.target_x, Direction.LEFT.value)
        self.assertEqual(self.gun.target_y, Direction.UP.value)

    def test_set_target_right_up(self):
        """set_target() works for RIGHT/UP combination."""
        self.gun.set_target(Direction.RIGHT, Direction.UP)
        self.assertEqual(self.gun.target_x, Direction.RIGHT.value)
        self.assertEqual(self.gun.target_y, Direction.UP.value)


if __name__ == '__main__':
    unittest.main()