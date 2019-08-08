import pygame
from caracters import Human,Goblin
from environment import Nature
from random import randrange


pygame.init()
clock = pygame.time.Clock()


e = Nature()
e.play_sound()

g = Goblin(e,x=520,y=410,dir='left')
g.walk(-50)
g2= Goblin(e,x = 450,dir='left')
g2.walk(-3)
g3 = Goblin(e,x = 390,dir='left')
g3.walk(-1)
g4 = Goblin(e,x = 370,dir='left')
g4.walk(-1)
g5 = Goblin(e,x = 350,dir='left')
g5.walk(-1)
h = Human(e,x=200)


def redrawWindow():
    e.draw()
    h.draw()
    g.draw()
    g2.draw()
    g3.draw()
    g4.draw()
    g5.draw()
    pygame.display.update()





speed = 100
direction =-1

run = True
while run:

    pygame.time.delay(50)



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        h.walk(-5)
    if keys[pygame.K_RIGHT]:
        h.walk(5)
    if keys[pygame.K_DOWN]:
        #y += vel
        h.bend(1)
    if keys[pygame.K_UP]:
        # y -= vel
        h.jump(10)


    if  g5.position_x  <=0:
        direction = 1
    elif g3.position_x>=600:
        direction = -1

    g3.walk(1.3*randrange(10)*direction)
    g2.walk(1.2*randrange(10)*direction)
    g.jump(randrange(10)*direction)
    g4.walk(1.4*randrange(10)*direction)
    g5.walk(1.5*randrange(10)*direction)
    g.walk(direction)


    redrawWindow()
clock.tick(100)
pygame.quite()
