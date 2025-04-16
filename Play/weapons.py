import pygame
from enum import Enum
from typing import List, Optional


# Direction Enum
class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    UP = -1
    DOWN = 1
    NONE = 0


# Physics Object (simplified implementation)
class ObjectProp:
    def __init__(self, surface_x: float = 0, surface_y: float = 0,
                 command_update=None, command_stop=None):
        self.x = surface_x
        self.y = surface_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.5
        self.command_update = command_update
        self.command_stop = command_stop
        self.active = True

    def throw(self, velocity_y: float, velocity_x: float):
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def update(self):
        if not self.active:
            return

        # Apply gravity
        self.velocity_y += self.gravity

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Call update callback
        if self.command_update:
            self.command_update(self)

        # Check if bullet went off-screen
        if self.y > 600 or self.x < 0 or self.x > 800:  # Example screen bounds
            self.active = False
            if self.command_stop:
                self.command_stop(self)


# Bullet Class
class Bullet:
    def __init__(self):
        self.position_x = 0
        self.position_y = 0
        self.size = 3
        self.color = (0, 0, 0)

    def draw(self, screen):
        object_position_y = int(screen.get_height() - self.position_y)
        object_position_x = int(self.position_x)
        pygame.draw.circle(screen, self.color, (object_position_x, object_position_y), self.size)


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
        self.__target_x = Direction.LEFT.value
        self.__target_y = Direction.UP.value
        self.power = 8
        self.bullets: List[Bullet] = []
        self.bullets_moving: List[Bullet] = []
        self.physics_objects: List[ObjectProp] = []
        self.cooldown = 0
        self.max_cooldown = 10  # frames between shots

    @property
    def velocity_x(self) -> float:
        return self.__velocity_x

    @velocity_x.setter
    def velocity_x(self, x: float):
        self.__velocity_x = x * self.target_x

    @property
    def velocity_y(self) -> float:
        return self.__velocity_y

    @velocity_y.setter
    def velocity_y(self, y: float):
        self.__velocity_y = y * self.target_y

    @property
    def target_x(self) -> int:
        return self.__target_x

    @target_x.setter
    def target_x(self, x: Direction):
        self.__target_x = x.value
        self.velocity_x = abs(self.velocity_x) * self.__target_x

    @property
    def target_y(self) -> int:
        return self.__target_y

    @target_y.setter
    def target_y(self, y: Direction):
        self.__target_y = y.value
        self.velocity_y = abs(self.velocity_y) * self.__target_y

    def set_target(self, target_x: Direction = Direction.LEFT, target_y: Direction = Direction.UP):
        self.target_x = target_x
        self.target_y = target_y

    def draw(self):
        # Draw all moving bullets
        for bullet in self.bullets_moving:
            bullet.draw(self._environment)

    def load(self, bullets: int = 1):
        for _ in range(bullets):
            self.bullets.append(Bullet())

    def bullet_drop(self):
        if self.bullets:
            self.bullets_moving.append(self.bullets.pop())

    def activate(self, position_y=0, position_x=0):
        if self.cooldown > 0:
            return

        if not self.bullets:
            print('Gun out of ammo')
            return

        self.bullet_drop()
        bullet_index = len(self.bullets_moving) - 1

        prop = ObjectProp(
            surface_x=position_x,
            surface_y=position_y,
            command_update=lambda prop, idx=bullet_index: self.update_position(prop, idx),
            command_stop=lambda prop, idx=bullet_index: self.stop_position(prop, idx)
        )
        prop.throw(self.velocity_y, self.velocity_x)
        self.physics_objects.append(prop)
        self.cooldown = self.max_cooldown

    def update_position(self, prop: ObjectProp, bullet_index: int):
        if bullet_index < len(self.bullets_moving):
            self.bullets_moving[bullet_index].position_x = prop.x
            self.bullets_moving[bullet_index].position_y = prop.y

    def stop_position(self, prop: ObjectProp, bullet_index: int):
        if bullet_index < len(self.bullets_moving):
            self.bullets_moving.pop(bullet_index)
        if prop in self.physics_objects:
            self.physics_objects.remove(prop)

    def update(self):
        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

        # Update physics objects
        for prop in self.physics_objects[:]:  # Use slice copy to safely modify during iteration
            prop.update()


# Main Game
class Game:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Gun Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.background = (255, 255, 255)
        self.gun = Gun(environment=self.screen)
        self.gun.load(100)
        self.gun.set_target(Direction.RIGHT, Direction.UP)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Fire from middle-bottom of screen
            self.gun.activate(position_y=100, position_x=self.width // 2)

    def update(self):
        self.gun.update()

    def render(self):
        self.screen.fill(self.background)
        self.gun.draw()
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