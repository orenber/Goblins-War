import pygame
from caracters import Human,Goblin
from environment import Nature
import numpy as np
import random


pygame.init()
clock = pygame.time.Clock()


e = Nature()
#e.play_sound()

g = Goblin(e,x=520,y=50,dir='left')
g.walk(-50)
g2 = Goblin(e,x = 450,dir='left')
g2.walk(-3)
g3 = Goblin(e,x = 390,dir='left')
g3.walk(-1)
g4 = Goblin(e,x = 370,dir='left')
g4.walk(-1)
g5 = Goblin(e,x = 350,dir='left')
g5.walk(-1)
h = Human(e,x=200, y =60)


def check_collide(hero:list ,enemy:list):

    # get array of enemy position

    # calculate the distance of the enemy from the hero in x axis
    x_distance = np.array([abs(n.position_x - hero.position_x) for n in enemy])
    # calculate the distance of the enemy from the hero in y axis
    y_distance = np.array([abs(n.position_y - hero.position_y) for n in enemy])
    # if the r is collide show text on screen " collide "
    index_enemy_collide = (y_distance < 5) & (x_distance < 5)

    collide = True in index_enemy_collide

    if collide:
        index = np.where(index_enemy_collide == True)
        enemy_num = str(index[0]+1)
        print("collide goblins number: " + enemy_num)
        enemy_collide = list(np.array(enemy)[index[0]])
    else:
        enemy_collide = []

    pass
    collide_state = {'state': collide, 'enemy_collide': enemy_collide}
    return collide_state

def live_bar(screen,health):
    hitbox = (100, 36,100, 100)
    pygame.draw.rect( screen, (0, 255, 0), (hitbox[0], hitbox[1] - 20, 80, 20) )
    pygame.draw.rect( screen, (255, 0, 0), (hitbox[0], hitbox[1] - 20, 80 - 79 * health / 100, 20) )

def enemy_action(enemy: Goblin, hero):

    # chuse randomaly the enemy action
    # generate random number between 1- 4
    random_number = random.randint(1, 4)
    # escape - change direction
    if random_number == 1:
        enemy.jump(40,5*direction)
    elif random_number == 2:
        enemy.attack()
        hero.health = -enemy.power

    pass
def enemy_wounded(enemy: Goblin, wepon):

    enemy.health -= wepon.power
def redrawWindow():

    e.draw()
    e.move_background()
    live_bar( e.win, h.health )

    text_score = font.render('Score: ' + str(score), 1, (0,0,0))
    health_score = font.render('Health:        ' + str(h.health), 1, (0,0,0))

    if h.health <=0:
        game_over = font_game_over.render('GAME OVER', 1, (10, 128, 147))
        font_game_over.set_bold(15)
        e.win.blit( game_over, (e.width/4, e.high/3) )


    e.win.blit(text_score,(e.width-150,10))
    e.win.blit(health_score, (20, 10) )

    h.draw()
    h.weapon.draw()

    g.draw()
    g.weapon.draw()
    g2.draw()
    g2.weapon.draw()
    g3.draw()
    g3.weapon.draw()
    g4.draw()
    g4.weapon.draw()
    g5.draw()
    g5.weapon.draw()

    pygame.display.update()


score = 0
speed = 100
direction =-1
# create font object
font = pygame.font.SysFont( "comicsansms", 22 )
font_game_over = pygame.font.SysFont( "comicsansms",40 )

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
        h.stop()
    if keys[pygame.K_UP]:
        # y -= vel
        h.jump(50,5)
    if keys[pygame.K_SPACE]:

        h.attack()


    if  g5.position_x  <=0:
        direction = 1
    elif g3.position_x>=600:
        direction = -1

    collide = check_collide(h, [g, g2, g3, g4, g5])

    if collide['state']:
        enemy_action(collide['enemy_collide'][0],h)
    bullets_moving = len( h.weapon.bullets_moving )
    print('bullets_moving: '+ str(bullets_moving))
    #if bullets_moving>0:
        #enemy_collide_wepon = check_collide(h.weapon.bullets_moving[0], [g, g2, g3, g4, g5] )
        #if enemy_collide_wepon['state']:
            #enemy_wounded(collide['enemy_collide'][0], h.weapon)




    g3.walk(2*direction)
    g2.walk(2*direction)
    g4.walk(4*direction)
    g5.walk(direction)
    g.walk(direction)


    redrawWindow()
clock.tick(100)
pygame.quite()
