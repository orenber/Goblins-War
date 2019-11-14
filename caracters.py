import pygame
import os
from physics import ObjectProp
from weapons import Gun
from Utility import is_member ,Direction


class Human(object):

    def __init__(self, environment, **attr):


        # private attribute
        self.__width = 0
        self.__high = 0
        self.__size_factor = 1 / 3
        self.__environment = environment
        self.__isJump = False
        self.__images_path = ''
        self.__walkCount = 0
        self.__position_y = 0
        self.__health = 100

        # public attribute
        # public attribute

        self.power =  0
        self.high = 180
        self.width = 60
        self.position_x = 200
        self.position_y = 0
        self.position_z = 0
        self.hitbox = (self.position_x + 17, self.position_y + 2, 31, 57)

        self.images_path = None
        self.__isJump = False
        self.jumpCount = 10
        self.move_direction = 'center'
        self.walk_direction = 'right'
        self.physics_state = ObjectProp()
        self.physics_state.command = lambda prop: self.update_position( prop )
        self.weapon = Gun(environment)

        self.bg = environment.background

        self.set_setup(**attr)
        # create human
        self.create()

    def set_setup(self, **prop):

        default = {'x':  200, 'y': 0, 'high': 180, 'width': 60, 'z': 0, 'dir': 'right'}
        fileds = list(prop.keys())
        state = is_member(fileds, default.keys())

        assert state, 'thar is no such member '
        # setup = default.copy()
        # setup.update(prop)
        for name in prop.keys():
            self.__setattr__(name, prop[name])

    @property
    def images_path(self)->str:
        return self.__images_path

    @images_path.setter
    def images_path(self, images_path: str=None):
        if images_path is None:

            self.__images_path = os.path.abspath(os.path.join(os.pardir,
                                                              'LikeBoss', 'Resources', 'images'))
        else:
            self.__images_path = images_path

    @property
    def high(self)->int:
        return self.__high

    @high.setter
    def high(self, high: int=180):

        self.__high = high*self.__size_factor

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, width: int):
        self.__width = width * self.__size_factor

    @property
    def position_y(self) -> int:
        return int(self.__position_y)

    @position_y.setter
    def position_y(self, y:int):
        if y < 0:
           y = 0
        new_position_y = self.high + y
        self.__position_y = new_position_y

    @property
    def health(self)->int:
        return   self.__health

    @health.setter
    def health(self,point):

        self.__health +=point
        if self.__health<=0:
            self.__health = 0
            self.dead()
        elif self.__health> 100:
            self.__health = 100





    def postion_on_canvas_y(self):
        new_position_y = self.__environment.win.get_height() - self.position_y
        return new_position_y

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

        self.standing = self.load_image('standing.png')

        pass


    def heal_bar(self):
        self.hitbox = (self.position_x + 17, self.postion_on_canvas_y() + 2, 31, 57)
        pygame.draw.rect( self.__environment.win, (0, 255, 0), (self.hitbox[0], self.hitbox[1] - 20, 50, 3) )
        pygame.draw.rect( self.__environment.win, (255, 0, 0), (self.hitbox[0], self.hitbox[1] - 20, 50-49*self.health/100, 3) )

    def draw(self):

        self.heal_bar()

        if abs(self.__walkCount) >= 27:
            self.__walkCount = 0


        if self.move_direction == 'left':

            self.walk_direction = 'left'
            self.__environment.win.blit( self.walkLeft[self.__walkCount // 3],
                                             (self.position_x, self.postion_on_canvas_y()) )
            self.__walkCount -= 1

        elif self.move_direction == 'right':

            self.walk_direction = 'right'
            self.__environment.win.blit(self.walkRight[self.__walkCount // 3],
                                   (self.position_x, self.postion_on_canvas_y()))
            self.__walkCount += 1

        else:

            self.__walkCount = 0
            if self.walk_direction == 'left':
                self.__environment.win.blit(self.walkLeft[self.__walkCount],
                                            (self.position_x, self.postion_on_canvas_y()))

            elif self.walk_direction == 'right':
                self.__environment.win.blit(self.walkRight[self.__walkCount],
                                            (self.position_x, self.postion_on_canvas_y()))
            elif self.move_direction == 'down':

                self.__environment.win.blit( self.standing[self.__walkCount],
                                             (self.position_x, self.postion_on_canvas_y()) )

    def walk(self, x_steps=1, z_steps=0):
        self.position_x += x_steps
        self.position_z += z_steps
        if x_steps > 0:
            self.move_direction = 'right'
        elif x_steps < 0:
            self.move_direction = 'left'
        pass

    def jump(self, y_high=5, x_steps=0,surface = 0):

        if not self.physics_state.rt.is_running:

            self.physics_state.set_setup(x=self.position_x, y=self.postion_on_canvas_y(), surface_x= self.position_x)
            move_direction = {'right': 1, 'left': -1, 'center': 0, 'down': 0}

            sign = move_direction[self.move_direction]
            self.physics_state.throw(x_steps*sign, y_high)



        pass

    def stop(self, y_high: int=1):
        self.move_direction = 'down'
        pass

    def attack(self):
        self.weapon.load(2)
        # get walk direction
        # set weapon target on the move direction
        move_direction = Direction[self.move_direction]
        self.weapon.set_target(move_direction)
        # activate weapon
        pos_y = self.position_y-self.high/2
        pos_x = self.position_x+self.width*1.5
        self.weapon.activate(pos_y, pos_x)
        pass

    def dead(self):

        self.move_direction = 'center'
        self.walk_direction == 'center'

        pass

    def update_position(self, prop):
        self.position_x = prop.x
        self.position_y = prop.y
        pass


class Goblin(Human):

    def __init__(self, environment, **attr):
        super().__init__(environment, **attr)


        # create goblin
        self.power = 3
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
        self.char = self.load_image( 'standing.png' )
        pass