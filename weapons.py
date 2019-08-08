import pygame
import os


class Weapons( object ):

    def __init__(self, owner, **attr):

        self.owner = owner
        self.velocity = 0
        self.power = 0


class Gun(Weapons):

    def __init__(self, owner, **attr):

        self.owner = owner
        self.velocity = 10
        self.power = 8
        self.bullets =[]

    def create(self):
        pass

    def update_animation(self):
        pass

    def load(self, bullets:int=1):
        for i in bullets:
            self.bullets.append(Bullet)
        pass

    def shout(self):
        for bullet in self.bullets:

            if bullet.x < 500 and bullet.x > 0:

                bullet.x += bullet.velocity
            else:
                self.bullets.pop(self.bullets.index(bullet))

        self.update_animation()



class Bullet(Weapons):

    def __init__(self):

        self.x = 7
        self.y = 6
        self.velocity = 1











