import pygame
from Play.physics import ObjectProp
from Utility import Direction


class Weapons( object ):

    def __init__(self, environment = None, owner=None, **attr):

        self.owner = owner
        self.velocity = 0
        self.power = 0
        self._environment = environment


class Gun(Weapons):

    def __init__(self, environment = None, **attr):
        super().__init__(environment, **attr)

        self.__velocity_x = 20
        self.__velocity_y = 20
        self.__target_x = Direction['left']
        self.__target_y = Direction['up']
        self.power = 8
        self.bullets = []
        self.bullets_moving = []
        self.physics_objects = []

    @property
    def velocity_x(self)->float:
        return self.__velocity_x

    @velocity_x.setter
    def velocity_x(self, x: float):
        self.__velocity_x = x * self.target_x

    @property
    def velocity_y(self)->float:
        return self.__velocity_y

    @velocity_y.setter
    def velocity_y(self, y: float):
        self.__velocity_y = y * self.target_x

    @property
    def target_x(self)->int:
        return self.__target_x

    @target_x.setter
    def target_x(self, x: Direction):
        self.__target_x = x.value
        self.velocity_x = abs(self.velocity_x)*self.__target_x

    @property
    def target_y(self)->int:
        return self.__target_y

    @target_y.setter
    def target_y(self, y: Direction):
        self.__target_y = y.value
        self.velocity_y = abs(self.velocity_y) * self.__target_y

    def set_target(self, target_x: Direction = Direction['left'], target_y: Direction = Direction['up']):
        self.target_x = target_x
        self.target_y = target_y

    def create(self):
        pass

    def draw(self):

        # draw gun

        # draw bullets
        bullets_num = len( self.bullets_moving )
        if bullets_num > 0:
            for n in range(bullets_num):
                self.bullets_moving[n].draw(self._environment.win)
        pass

    def load(self, bullets: int = 1):
        for i in range(bullets):
            b = Bullet()
            self.bullets.append(b)
        pass

    def bullet_drop(self):

        self.bullets_moving.append(self.bullets[-1])
        self.bullets.pop()

    def activate(self, position_y=0, position_x=0):

        if len(self.bullets) > 0:

            self.physics_objects.append(ObjectProp(surface_y=position_y, surface_x=position_x,
                                        command=lambda prop: self.update_position(prop)))
            self.physics_objects[-1].throw(self.velocity_y, self.velocity_x)
            self.bullet_drop()
            if len(self.physics_objects) > 0:
                self.physics_objects.pop(0)

        else:
              print('gun out of ammo')

    def update_position(self, prop):
        bullets_num = len(self.bullets_moving )
        if bullets_num > 0:

            self.bullets_moving[0].position_x = prop.x
            self.bullets_moving[0].position_y = prop.y

        pass


class Bullet():

    def __init__(self):

        self.__position_x = 0
        self.__position_y = 0


        self.size = 3
        self.color = (0, 0, 0)

    @property
    def position_x(self) -> int:
        return self.__position_x

    @position_x.setter
    def position_x(self, x: int):

        self.__position_x = x

    @property
    def position_y(self) -> int:
        return self.__position_y

    @position_y.setter
    def position_y(self, y:int):
        if y < 0:
            y = 0
        new_position_y = int( y)

        self.__position_y = new_position_y

    def position_canvas_y(self,canvas):
        return canvas.get_height() - self.position_y


    def draw(self, screen):
        object_position_y = int(self.position_canvas_y(screen))
        object_position_x = int(self.position_x)
        pygame.draw.circle(screen, self.color, (object_position_x, object_position_y), self.size)


def screen():
    WHITE = (255, 255, 255)
    (width, height) = (600, 400)
    pygame.init()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("TUFF")
    screen.fill(WHITE)

    return screen


def main():
    e = screen()
    gun = Gun()
    gun.load(100)


    running = True

    while running:
        pygame.time.delay(50)
        gun.draw(e)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            gun.activate()
        pygame.display.update()


if __name__ == '__main__':
    main()