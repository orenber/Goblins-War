import pygame
import os


class Nature:

    def __init__(self):

        self.__images_path = ''
        self.__background = ''

        self.background = ''
        self.sound = False
        self.width = 700
        self.high = 500

        self.images_path = ['LikeBoss', 'Resources', 'images']
        self.sound_path = ['LikeBoss', 'Resources', 'sound']
        self.__background_file = 'bg.jpg'
        self.__music_file = 'music.mp3'
        self.create()

        pass

    def create(self):
        # show display figure
        self.background = self.load_image(self.__background_file)
        self.win = pygame.display.set_mode((self.width, self.high))
        self.draw()
        pass

    def draw(self):
        self.win.fill((0, 0, 0))
        self.win.blit(self.background, (0, 0))
        #pygame.display.update()


    @property
    def images_path(self)->str:
        return self.__images_path

    @images_path.setter
    def images_path(self, images_path: tuple):

        self.__images_path =  os.path.abspath(os.path.join(os.pardir, *images_path))
    pass

    @property
    def sound_path(self)->str:
        return self.__sound_path

    @sound_path.setter
    def sound_path(self, sound_path: tuple):

        self.__sound_path = os.path.abspath( os.path.join( os.pardir, *sound_path))




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
            file = self.__music_file
        path = os.path.join(self.sound_path, file)
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1, 0.0)
        pass





