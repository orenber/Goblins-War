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

    def activate(self):
        for bullet in self.bullets:


            bullet.x += bullet.velocity

            self.bullets.pop(self.bullets.index(bullet))

        self.update_animation()



class Bullet():

    def __init__(self):

        self.x = 7
        self.y = 6
        self.velocity = 1

    def shout(self,x,y):
        pygame.draw.circle('')













