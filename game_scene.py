import pygame
from Play.caracters import Human,Goblin
from Play.environment import Nature
import numpy as np
import random
from Utility import is_member ,Direction,full_file


pygame.init()
clock = pygame.time.Clock()


e = Nature()
#e.play_sound()


g = []
number_of_enemy = 10
for n in range(number_of_enemy):
    random_position_x = random.randint(400,1000)
    random_position_y = random.randint(0,80)
    enemy = Goblin( e, position_x=random_position_x,position_y = random_position_y, walk_direction='left' )
    enemy.create()
    random_speed = random.randint(-5,-1 )
    enemy.walk( random_speed )
    g.append(enemy)


h = Human(e,position_x=200, position_y = 60)
h.create()

def check_collide(hero: list, enemy: list):
    collide_distance_x = []
    collide_distance_y = []
    distance_jump_collide = []

    # get array of enemy position
    for j in enemy:
        if j.position_x < h.position_x:
            # calculate the distance of the enemy from the hero in x axis
            collide_distance_x.append(abs(j.position_x + j.width - hero.position_x))
        else:
            collide_distance_x.append(abs(h.position_x + h.width - j.position_x))
        # calculate the distance of the enemy from the hero in y axis
        collide_distance_y.append(abs(j.position_y - hero.position_y))
        # jump collide
        distance_jump_collide.append(abs(j.position_y + j.high - hero.position_y))
    x_distance = np.array(collide_distance_x)
    y_distance = np.array(collide_distance_y)
    distance_jump_collide = np.array(distance_jump_collide)

    # if the r is collide show text on screen " collide "
    index_enemy_collide = (y_distance < 5) & (x_distance < 5)
    index_jump_collide  = (distance_jump_collide <10)& (x_distance < 5)
    jump_collide = True in index_jump_collide
    Enemy_collide = True in index_enemy_collide
    enemy_collide = []

    if Enemy_collide:
        collide = Enemy_collide
        index = np.where(index_enemy_collide == True)
        # enemy_num = str(index[0]+1)
        # print("collide goblins number: " + enemy_num)
        enemy_collide = list(np.array(enemy)[index])
        injure = 'Hero'
    elif jump_collide:
        collide = jump_collide
        index = np.where( index_jump_collide == True )
        # enemy_num = str( index[0] + 1 )
        # print( "jump_collide  goblins number: " + enemy_num )
        enemy_collide = list( np.array( enemy )[index] )
        injure = 'Enemy'
    else:
        collide = False
        injure = None

    pass
    collide_state = {'state': collide, 'injure': injure ,'enemy_collide': enemy_collide}
    return collide_state


def live_bar(screen, health):
    hit_box = (100, 36, 100, 100)
    pygame.draw.rect(screen, (0, 255, 0), (hit_box[0], hit_box[1] - 20, 80, 20))
    pygame.draw.rect(screen, (255, 0, 0), (hit_box[0], hit_box[1] - 20, 80 - 79 * health / 100, 20))


def enemy_action(enemy: Goblin, hero, injure):

    if injure == 'Hero':
        # cause randomly the enemy action
        # generate random number between 1- 4
        random_number = random.randint(1, 4)
        # escape - change direction
        if random_number == 1:
            enemy.jump(40, 5* - Direction[enemy.walk_direction].value )
        elif random_number == 2:
            enemy.stop()
            enemy.attack()
            hero.health = -enemy.power

        elif random_number == 3:
            enemy.stop()

        pass
    elif injure == 'Enemy':
        enemy.health = -hero.power
        if enemy.health == 0:
            voice = enemy.sound_dead
        else:
            voice = enemy.sound_hooch

        enemy.play_sound(voice)
        enemy.jump( 40, 5 * direction )


def control_character(character):

    keys = pygame.key.get_pressed()
    if character.live:
        if keys[pygame.K_LEFT]:
            character.walk(-5)
        if keys[pygame.K_RIGHT]:
            character.walk(5)
        if keys[pygame.K_DOWN]:
            character.stop()
        if keys[pygame.K_UP]:
            character.jump(50, 5)
        if keys[pygame.K_SPACE]:
            character.attack()


def redrawWindow():

    e.draw()
    e.move_background()
    live_bar(e.win, h.health)

    text_score = font.render('Score: ' + str(score), 1, (0,0,0))
    health_score = font.render('Health:        ' + str(h.health), 1, (0,0,0))
    time_left = max(round(sp),0)
    time_left_font = font.render('Time:' + str(time_left), 1, (0,0,0))
    if (not h.live) or time_left == 0:
        game_over = font_game_over.render('GAME OVER', 1, (10, 128, 147))

        e.win.blit(game_over, (e.width/4, e.high/3))

    elif enemy_alive == 0:
        game_over = font_game_over.render('YOU WIN!', 1, (12, 250, 147))

        e.win.blit(game_over, (e.width/4, e.high/3))

    e.win.blit( text_score, (e.width - 150, 10) )
    e.win.blit( health_score, (20, 10) )
    e.win.blit( time_left_font, (200, 10) )
    h.draw()
    [r.draw() for r in g]


    pygame.display.update()

sp = 60
score = 0
speed = 100
direction =-1
# create font object
font = pygame.font.SysFont("comicsansms", 22 )
font_game_over = pygame.font.SysFont("comicsansms",40 )
font_game_over.set_bold( 15 )
random_speed = [random.randint( 1, 4 ) for i in range(number_of_enemy)]
run = True
while run:

    pygame.time.delay(50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    control_character(h)

    if g[-1].position_x <=0:
        direction = 1
    elif g[0].position_x>=600:
        direction = -1

    collide = check_collide(h, g)

    if h.live:
        if collide['state']:
            enemy_action( collide['enemy_collide'][0], h, collide['injure'] )
            if collide['injure'] == 'Enemy':
                score += 20
            [e.walk( random_speed[i] * direction ) for i, e in enumerate( g, 0 ) if not collide['enemy_collide'][0] ]
        else:
            [e.walk(random_speed[i]*direction) for i, e in enumerate(g,0)]
    if not h.live:
        # all the goblins are celabrate
        [r.jump(30) for r in g if 0 < r.position_x < e.width]

    enemy_alive = np.sum([e.live for e in g])
    sp -= 1/60
    redrawWindow()
clock.tick(100)
pygame.quit()
