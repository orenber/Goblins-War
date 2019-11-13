import pygame
from caracters import Human,Goblin
from environment import Nature
from random import randrange


pygame.init()
clock = pygame.time.Clock()


e = Nature()
#e.play_sound()

g = Goblin(e,x=520,y=10,dir='left')
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
h1 = Human(e,x=300)


def redrawWindow():
    e.draw()
    text_score = font.render('Score: ' + str(score), 1, (0,0,0))
    e.win.blit(text_score,(490,10))

    h.draw()
    h1.draw()
    h.weapon.draw()
    g.draw()
    g2.draw()
    g3.draw()
    g4.draw()
    g5.draw()
    pygame.display.update()




score = 0
speed = 100
direction =-1
# create font object
font = pygame.font.SysFont('comicsans', 30, True)

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
        h.jump(50,5)
    if keys[pygame.K_SPACE]:

        h.attack()


    if  g5.position_x  <=0:
        direction = 1
    elif g3.position_x>=600:
        direction = -1

    g3.walk(2*direction)
    g2.walk(2*direction)
    g.jump(40,5*direction)
    g4.walk(4*direction)
    g5.walk(direction)
    g.walk(direction)


    redrawWindow()
clock.tick(100)
pygame.quite()
