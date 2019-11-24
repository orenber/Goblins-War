from unittest import TestCase
from Play.environment import Nature
import pygame


class TestNature( TestCase ):

    def setUp(self):
        self.nature = Nature()


    def test_draw(self):
        pygame.init()

        while True:
            pygame.time.delay( 50 )
            self.nature.draw()

            pygame.display.update()
    def test_move_background(self):
        pygame.init()

        while True:
            pygame.time.delay( 50 )
            self.nature.draw()
            self.nature.move_background()
            pygame.display.update()
    def test_images_path(self):
        self.fail()


    def test_sound_path(self):
        self.nature.sound()

    def test_background(self):
        self.fail()

    def test_load_image(self):
        self.fail()

    def test_play_sound(self):
       self.nature.play_sound()
       while True:
            pygame.time.delay( 50 )
            self.nature.draw()

            pygame.display.update()