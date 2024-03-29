import pygame
import os


class Nature:

    def __init__(self) -> object:

        self.__images_path = ''
        self.__background = ''

        self.background = ''
        self.sound = False
        self.width = 500
        self.high = 500

        self.bg_position_x1 = 0
        self.bg_position_y1 = 0
        self.bg_position_x2 = 0
        self.bg_position_y2 = 0

        self.images_path = ['Resources', 'images', 'Canvas']
        self.sound_path = ['Resources', 'sound']
        self.background_file = 'bg.jpg'
        self.music_file = 'music.mp3'
        self.__create()
        pass

    def __create(self):
        # show display figure
        self.background = self.load_image(self.background_file)
        self.bg_position_x2 = self.background.get_width()
        self.win = pygame.display.set_mode((self.width, self.high))
        self.draw()
        pass

    def draw(self):
        self.win.fill((0, 0, 0))
        self.win.blit(self.background, (self.bg_position_x1, self.bg_position_y1))
        self.win.blit(self.background, (self.bg_position_x2, self.bg_position_y2) )

    def move_background(self,speed:float = 1.4):

        self.bg_position_x1 -= speed
        self.bg_position_x2 -= speed

        if self.bg_position_x1<self.background.get_width()*-1:
            self.bg_position_x1 = self.background.get_width()
        if self.bg_position_x2 < self.background.get_width()* -1:
            self.bg_position_x2 = self.background.get_width()
        pass

    def position_on_canvas_y(self, position_y):
        new_position_y = self.win.get_height() - position_y
        return new_position_y


    @property
    def images_path(self)->str:
        return self.__images_path

    @images_path.setter
    def images_path(self, images_path: tuple):

        self.__images_path = os.path.abspath(os.path.join(*images_path))
    pass

    @property
    def sound_path(self)->str:
        return self.__sound_path

    @sound_path.setter
    def sound_path(self, sound_path: tuple):

        self.__sound_path = os.path.abspath(os.path.join(*sound_path))


    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, image_background):

        self.__background = image_background

    def load_image(self, file: str=None):

        path = os.path.join(self.images_path, file)
        image = pygame.image.load(path)
        return image

    def play_sound(self, file: str=None):

        if file is None:
            file = self.music_file
        path = os.path.join(self.sound_path, file)
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1, 0.0)
        pass





