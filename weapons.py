import pygame
from physics import ObjectProp
from time import sleep


class Weapons( object ):

    def __init__(self, owner=None, **attr):

        self.owner = owner
        self.velocity = 0
        self.power = 0


class Gun(Weapons):

    def __init__(self, **attr):
        super().__init__(None, **attr)
        self.velocity = 20
        self.power = 8
        self.bullets = []


    def create(self):
        pass

    def draw(self, screen):

        # draw gun

        # draw bullets
        if len(self.bullets) > 0:
            self.bullets[-1].draw(screen)

        pass

    def load(self, bullets: int = 1):
        for i in range(bullets):
            b = Bullet()
            self.bullets.append(b)
        pass

    def activate(self):

        if len( self.bullets ) > 0:

            self.physics_object = ObjectProp( surface_y=50, surface_x=50 )
            self.physics_object.command = lambda prop: self.update_position( prop )
            self.physics_object.throw(70, 10)
            self.bullets.pop()

        else:
            print('gun out of ammo')


    def update_position(self, prop):
        if len(self.bullets) > 0:
            self.bullets[-1].x = prop.x
            self.bullets[-1].y = prop.y
        pass



class Bullet():

    def __init__(self):

        self.x = 70
        self.y = 30
        self.size = 3
        self.color = (0, 0, 0)

    def draw(self, screen):
        object_position_y = int(screen.get_height() - self.y)
        object_position_x = int(self.x)
        screen.fill((255, 255, 255))
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
            sleep(0.2)
            gun.activate()
        pygame.display.update()


if __name__ == '__main__':
    main()









