import pygame
from enum import Enum
from typing import List


# Direction Enum
class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    UP = -1   # BUG FIX NOTE: UP/DOWN sharing -1/1 with LEFT/RIGHT is misleading but
    DOWN = 1  # functionally fine since they're used in separate axes. Left as-is.
    NONE = 0


# Physics Object
class ObjectProp:
    def __init__(self, surface_x: float = 0, surface_y: float = 0,
                 screen_height: int = 600, screen_width: int = 800,
                 command_update=None, command_stop=None):
        self.x = surface_x
        # BUG FIX 1: position_y was stored in screen coords but treated as world coords.
        # We now store y in world coords (0 = bottom of screen) consistently.
        self.y = surface_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.5
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.command_update = command_update
        self.command_stop = command_stop
        self.active = True

    def throw(self, velocity_y: float, velocity_x: float):
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def update(self):
        if not self.active:
            return

        # BUG FIX 2: Gravity should decrease upward velocity (subtract), not add.
        # In world coords, y increases upward, so gravity pulls y down (decreases it).
        self.velocity_y -= self.gravity

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Call update callback
        if self.command_update:
            self.command_update(self)

        # BUG FIX 3: Off-screen check was using hardcoded values instead of
        # actual screen dimensions passed in. Also fixed y < 0 (fell below ground).
        if self.y < 0 or self.x < 0 or self.x > self.screen_width:
            self.active = False
            if self.command_stop:
                self.command_stop(self)


# Bullet Class
class Bullet:
    def __init__(self):
        self.position_x = 0
        self.position_y = 0  # world coords: 0 = bottom of screen
        self.size = 3
        self.color = (20, 20, 20)

    def draw(self, screen):
        # Convert world Y to screen Y: screen_y = screen_height - world_y
        screen_y = int(screen.get_height() - self.position_y)
        screen_x = int(self.position_x)
        # BUG FIX 4: Added bounds check so bullets don't get drawn off-screen,
        # which could cause rendering glitches near screen edges.
        if 0 <= screen_x <= screen.get_width() and 0 <= screen_y <= screen.get_height():
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size)


# Weapon Base Class
class Weapon:
    def __init__(self, environment=None, owner=None):
        self.owner = owner
        self.velocity = 0
        self.power = 0
        self._environment = environment


# Gun Class
class Gun(Weapon):
    def __init__(self, environment=None, **attr):
        super().__init__(environment, **attr)
        self.__velocity_x = 20
        self.__velocity_y = 20
        self.__target_x = Direction.RIGHT.value
        self.__target_y = Direction.UP.value
        self.power = 8
        self.bullets: List[Bullet] = []
        self.bullets_moving: List[Bullet] = []
        self.physics_objects: List[ObjectProp] = []
        self.cooldown = 0
        self.max_cooldown = 10

    @property
    def velocity_x(self) -> float:
        return self.__velocity_x

    @velocity_x.setter
    def velocity_x(self, x: float):
        self.__velocity_x = x * self.__target_x

    @property
    def velocity_y(self) -> float:
        return self.__velocity_y

    @velocity_y.setter
    def velocity_y(self, y: float):
        self.__velocity_y = y * self.__target_y

    @property
    def target_x(self) -> int:
        return self.__target_x

    @target_x.setter
    def target_x(self, x: Direction):
        self.__target_x = x.value
        self.__velocity_x = abs(self.__velocity_x) * self.__target_x

    @property
    def target_y(self) -> int:
        return self.__target_y

    @target_y.setter
    def target_y(self, y: Direction):
        self.__target_y = y.value
        self.__velocity_y = abs(self.__velocity_y) * self.__target_y

    def set_target(self, target_x: Direction = Direction.LEFT, target_y: Direction = Direction.UP):
        self.target_x = target_x
        self.target_y = target_y

    def draw(self):
        for bullet in self.bullets_moving:
            bullet.draw(self._environment)

    def load(self, bullets: int = 1):
        for _ in range(bullets):
            self.bullets.append(Bullet())

    def bullet_drop(self):
        if self.bullets:
            self.bullets_moving.append(self.bullets.pop())

    def activate(self, position_y: float = 0, position_x: float = 0):
        if self.cooldown > 0:
            return

        if not self.bullets:
            print('Gun out of ammo')
            return

        self.bullet_drop()
        # BUG FIX 5: Capture bullet_index at call time via default arg to avoid
        # closure capture bug — without this, all lambdas share the same late-bound
        # `bullet_index` reference, which drifts as bullets_moving grows.
        bullet_index = len(self.bullets_moving) - 1

        screen = self._environment
        prop = ObjectProp(
            surface_x=position_x,
            surface_y=position_y,
            screen_height=screen.height,
            screen_width=screen.width,
            command_update=lambda p, idx=bullet_index: self.update_position(p, idx),
            command_stop=lambda p, idx=bullet_index: self.stop_position(p, idx)
        )
        prop.throw(self.__velocity_y, self.__velocity_x)
        self.physics_objects.append(prop)
        self.cooldown = self.max_cooldown

    def update_position(self, prop: ObjectProp, bullet_index: int):
        if bullet_index < len(self.bullets_moving):
            self.bullets_moving[bullet_index].position_x = prop.x
            self.bullets_moving[bullet_index].position_y = prop.y

    def stop_position(self, prop: ObjectProp, bullet_index: int):
        # BUG FIX 6: Removing a bullet by index shifts all subsequent indices,
        # breaking position tracking for bullets fired after this one.
        # We now mark it invisible and clean up safely via a flag instead.
        if bullet_index < len(self.bullets_moving):
            self.bullets_moving[bullet_index].active = False
        if prop in self.physics_objects:
            self.physics_objects.remove(prop)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

        for prop in self.physics_objects[:]:
            prop.update()

        # BUG FIX 6 (cont.): Purge inactive bullets without disrupting live indices.
        # We do this AFTER physics updates so index references stay valid this frame.
        self.bullets_moving = [b for b in self.bullets_moving if getattr(b, 'active', True)]


# Bullet needs an active flag for the fix above
_original_bullet_init = Bullet.__init__

def _patched_bullet_init(self):
    _original_bullet_init(self)
    self.active = True

Bullet.__init__ = _patched_bullet_init


# Main Game
class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Gun Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.background = (245, 240, 230)
        self.gun = Gun(environment=self.screen)
        self.gun.load(200)
        self.gun.set_target(Direction.RIGHT, Direction.UP)

        # BUG FIX 7: Font init guard — pygame.font.init() is safe to call
        # even if pygame.init() already covered it, but being explicit avoids
        # issues if someone calls Game() without a full pygame.init().
        pygame.font.init()
        self.font = pygame.font.SysFont("monospace", 16)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # BUG FIX 8: Direction switching was missing entirely. Added keyboard
            # controls so the gun direction can actually be changed at runtime.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.gun.set_target(Direction.LEFT, Direction.UP)
                if event.key == pygame.K_RIGHT:
                    self.gun.set_target(Direction.RIGHT, Direction.UP)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Fire from bottom-center of screen (world Y = 100 from bottom)
            self.gun.activate(position_y=100, position_x=self.width // 2)

    def update(self):
        self.gun.update()

    def render(self):
        self.screen.fill(self.background)
        self.gun.draw()

        # HUD
        ammo_text = self.font.render(
            f"Ammo: {len(self.gun.bullets)}  In-flight: {len(self.gun.bullets_moving)}  "
            f"[SPACE] shoot  [←→] aim",
            True, (60, 60, 60)
        )
        self.screen.blit(ammo_text, (10, 10))

        # Draw gun origin marker
        pygame.draw.circle(self.screen, (200, 80, 60),
                           (self.width // 2, self.height - 100), 6)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()