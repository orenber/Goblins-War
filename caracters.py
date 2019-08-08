import pygame
import os


class Human(object):

    def __init__(self, environment, **attr):

        setup = self.set_setup(attr)
        # private attribute
        self.__width = 0
        self.__high = 0
        self.__size_factor = 1 / 3
        self.__environment = environment
        self.__isJump = False
        self.__images_path = ''
        self.__walkCount = 0

        # public attribute
        self.position_x = setup['x']
        self.position_y = setup['y']
        self.position_z = setup['z']
        self.high = setup['high']
        self.width = setup['width']

        self.images_path = None
        self.jumpCount = 10
        self.move_direction = 'center'
        self.walk_direction = setup['dir']

        self.bg = environment.background

        # create human
        self.create()


    def set_setup(self, prop: dict)->dict:

        default = {'x':  200, 'y': 400, 'high': 180, 'width': 60, 'z': 0, 'dir': 'right'}
        setup = default.copy()
        setup.update(prop)
        return setup

    @property
    def images_path(self)->str:
        return self.__images_path

    @images_path.setter
    def images_path(self, images_path: str=None):
        if images_path is None:

            self.__images_path = os.path.abspath(os.path.join(os.pardir,
                                                              'BossGame', 'Resources', 'images'))
        else:
            self.__images_path = images_path

    @property
    def high(self)->int:
        return self.__high

    @high.setter
    def high(self, high: int):

        self.__high = high*self.__size_factor

    @property
    def width(self) -> int:
        return self.__high

    @width.setter
    def width(self, width: int):
        self.__width = width * self.__size_factor

    def load_image(self, file: str=''):

        path = os.path.join(self.images_path, file)
        image = pygame.image.load(path)
        return image

    def create(self):

        self.walkRight = [self.load_image('R1.png'), self.load_image('R2.png'), self.load_image( 'R3.png'),
                    self.load_image('R4.png'), self.load_image('R5.png'), self.load_image('R6.png'),
                    self.load_image('R7.png'), self.load_image('R8.png'),  self.load_image('R9.png')]

        self.walkLeft = [self.load_image('L1.png'), self.load_image('L2.png'), self.load_image('L3.png'),
                   self.load_image('L4.png'), self.load_image('L5.png'), self.load_image('L6.png'),
                   self.load_image('L7.png'), self.load_image('L8.png'), self.load_image('L9.png')]

        self.char = self.load_image('standing.png')
        pass

    def draw(self):

        if abs(self.__walkCount) >= 27:
            self.__walkCount = 0


        if self.move_direction == 'left':

            self.walk_direction = 'left'
            self.__environment.win.blit( self.walkLeft[self.__walkCount // 3],
                                             (self.position_x, self.position_y) )
            self.__walkCount -= 1

        elif self.move_direction == 'right':

            self.walk_direction = 'right'
            self.__environment.win.blit(self.walkRight[self.__walkCount // 3],
                                   (self.position_x, self.position_y))
            self.__walkCount += 1

        else:

            self.__walkCount = 0
            if self.walk_direction == 'left':
                self.__environment.win.blit(self.walkLeft[self.__walkCount],
                                            (self.position_x, self.position_y))

            elif self.walk_direction == 'right':
                self.__environment.win.blit(self.walkRight[self.__walkCount],
                                            (self.position_x, self.position_y))



    def walk(self, x_steps=1, z_steps=0):
        self.position_x += x_steps
        self.position_z += z_steps
        if x_steps > 0:
            self.move_direction = 'right'
        elif x_steps < 0:
            self.move_direction = 'left'
        pass

    def jump(self, y_high=5, x_steps=0):

        if not self.__isJump:

            if self.jumpCount >= -10:
                neg = 1
                if self.jumpCount < 0:
                    neg = -1
                self.position_y -= (self.jumpCount ** 2)*0.5*neg
                self.jumpCount -= 1
            else:
                self.__isJump = False
                self.jumpCount = 10
            self.move_direction = 'up'

        pass

    def bend(self, y_high: int=1):
        self.position_y += y_high
        self.move_direction = 'down'
        pass

    def attack(self, weapon='hand'):
        pass

    def dead(self,cuse):
        pass


class Worker(Human):

    def __init__(self):
        pass


class Boss(Worker):

    def __init__(self):
        pass


class Programmer(Worker):

    def __init__(self):
        pass


class Goblin(Human):

    def __init__(self, environment, **attr):
        super().__init__(environment, **attr)


        # create goblin
        self.move_direction = 'center'
        self.walk_direction == 'left'
        self.create()


    def create(self):

        self.walkRight = [self.load_image( 'R1E.png' ), self.load_image( 'R2E.png' ), self.load_image('R3E.png'),
                    self.load_image( 'R4E.png' ), self.load_image('R5E.png'), self.load_image('R6E.png'),
                    self.load_image( 'R7E.png' ), self.load_image('R8E.png'),  self.load_image('R9E.png')]

        self.walkLeft = [self.load_image( 'L1E.png' ), self.load_image('L2E.png' ), self.load_image('L3E.png'),
                   self.load_image('L4E.png'), self.load_image('L5E.png' ), self.load_image('L6E.png'),
                   self.load_image('L7E.png'), self.load_image('L8E.png' ), self.load_image('L9E.png')]

        pass