import pygame
import os
from Play.physics import ObjectProp
from Play.weapons import Gun
from Utility import is_member ,Direction,full_file
from Utility.timer_utility import RepeatedTimer


class Human(object):
    # create human

    def __init__(self, environment, **attr):

        # private attribute
        self._environment = environment
        self._frame_count = 0

        self.__width = 0
        self.__high = 0
        self.__size_factor = 1 / 3
        self.__isJump = False
        self.__position_y = 0
        self.__health = 100
        self.__live = True
        self.__isJump = False

        # public attribute
        # public attribute

        self.power = 20
        self.high = 180
        self.width = 60
        self.position_x = 200
        self.position_y = 0
        self.position_z = 0
        self.hitbox = (self.position_x + 17, self.position_y + 2, 31, 57)

        self.images_path = full_file(['Resources', 'images', 'Hero'])
        self.sound_hit = full_file(['Resources', 'sound', 'hit.mp3'])


        self.jumpCount = 10
        self.move_direction = 'center'
        self.walk_direction = 'right'
        self.physics_state = ObjectProp()
        self.physics_state.command_update = lambda prop: self.update_position(prop)
        self.weapon = Gun(environment)

        self.set_setup(**attr)

    def set_setup(self, **prop):

        default = ['position_x', 'position_y', 'high', 'width', 'walk_direction']
        fileds = list(prop.keys())
        (state, missing) = is_member(fileds, default)

        assert state, 'thar is no such member :' + str(missing)
        # setup = default.copy()
        # setup.update(prop)
        for name in prop.keys():
            self.__setattr__(name, prop[name])

    @property
    def live(self)->bool:
        if self.health > 0:
            self.__live = True
        else:
            self.__live = False

        return self.__live

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
    def position_y(self, y: int):
        if y < 0 & self.health > 0:
            y = 0
        new_position_y = self.high + y
        self.__position_y = new_position_y

    @property
    def health(self)->int:
        return self.__health

    @health.setter
    def health(self, point):

        self.__health += point
        if self.__health <= 0:
            self.__health = 0
            self.__dead()
        elif self.__health > 100:
            self.__health = 100

    def position_on_canvas_y(self):
        new_position_y = self._environment.win.get_height() - self.position_y
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

        self.standing = [self.load_image('standing.png')]

        pass

    def heal_bar(self):
        self.hitbox = (self.position_x + 17, self.position_on_canvas_y() + 2, 31, 57)
        pygame.draw.rect(self._environment.win, (0, 255, 0), (self.hitbox[0], self.hitbox[1] - 20, 50, 3))
        pygame.draw.rect(self._environment.win, (255, 0, 0),
                         (self.hitbox[0], self.hitbox[1] - 20, 50-49*self.health/100, 3))

    def draw(self):

        self.heal_bar()

        if abs(self._frame_count) >= 27:
            self._frame_count = 0

        if self.move_direction == 'left':

            self.walk_direction = 'left'
            self._environment.win.blit( self.walkLeft[self._frame_count // 3],
                                             (self.position_x, self.position_on_canvas_y()) )
            self._frame_count -= 1

        elif self.move_direction == 'right':

            self.walk_direction = 'right'
            self._environment.win.blit(self.walkRight[self._frame_count // 3],
                                   (self.position_x, self.position_on_canvas_y()))
            self._frame_count += 1
        elif self.move_direction == 'down':

            self._environment.win.blit(self.standing[0],
                                    (self.position_x, self.position_on_canvas_y()))

        else:

            self._frame_count = 0
            if self.walk_direction == 'left':
                self._environment.win.blit(self.walkLeft[ self._frame_count],
                                            (self.position_x, self.position_on_canvas_y()))

            elif self.walk_direction == 'right':
                self._environment.win.blit(self.walkRight[ self._frame_count],
                                            (self.position_x, self.position_on_canvas_y()))

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

            self.physics_state.set_setup(x=self.position_x, y=self.position_y,
                                         surface_x =self.position_x,surface_y = surface  )
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

        self.play_sound(self.sound_hit)
        pass

    def update_position(self, prop):
        self.position_x = prop.x
        self.position_y = prop.y
        pass

    def __dead(self):

        self.move_direction = 'down'
        # prepare the grave deep
        self.physics_state.set_setup(bottom=-1500)
        # jump to the grave
        self.jump(60)

        pass

    def play_sound(self, file_path: str=None):

        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(1, 0.0)



class Goblin(Human):

    def __init__(self, environment, **attr):
        super().__init__(environment, **attr)
        self.images_path = full_file(['Resources', 'images', 'Enemy'])

        # create goblin
        self.power = 3
        self.move_direction = 'center'
        self.walk_direction = 'left'
        self.high = 180

        self.sound_hooch = full_file(['Resources', 'sound', 'wound.mp3'])
        self.sound_dead = full_file(['Resources', 'sound', 'died.mp3'])
        self.__attack = False
        self.timer = RepeatedTimer()

    def create(self):

        self.walkRight = [self.load_image( 'R1E.png' ), self.load_image( 'R2E.png' ), self.load_image('R3E.png'),
                    self.load_image( 'R4E.png' ), self.load_image('R5E.png'), self.load_image('R6E.png'),
                    self.load_image( 'R7E.png' ), self.load_image('R8E.png'), self.load_image('R5E.png')]

        self.walkLeft = [self.load_image( 'L1E.png' ), self.load_image('L2E.png' ), self.load_image('L3E.png'),
                   self.load_image('L4E.png'), self.load_image('L5E.png' ), self.load_image('L6E.png'),
                   self.load_image('L7E.png'), self.load_image('L8E.png' ), self.load_image('L5E.png')]
        self.standing = [self.load_image('L1E.png')]

        self.attack_right =[self.load_image('R9E.png') , self.load_image('R10E.png'),self.load_image('R11E.png')]
        self.attack_left = [self.load_image('L9E.png') , self.load_image('L10E.png'),self.load_image('L11E.png')]


    def draw(self):


        if self.__attack == False:
            super().draw()

        elif self.__attack == True:
            self._frame_count += 1
            if self.move_direction == 'left':


                self._environment.win.blit( self.attack_left[self._frame_count % 3],
                                             (self.position_x, self.position_on_canvas_y()) )
            elif self.move_direction == 'right':

                self._environment.win.blit( self.attack_right[self._frame_count% 3],
                                             (self.position_x, self.position_on_canvas_y()) )


    def attack(self):

        self.timer.set_attr( timer_function=self.box_attack, start_input_args=[True],
                             stop_function=self.box_attack, stop_input_args=[False],
                             interval=0.1, limit=0.5)
        self.timer.start()

    def box_attack(self, state:bool=True):


        self.__attack = state

