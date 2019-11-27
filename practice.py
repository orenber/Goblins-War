import pygame
from Play.environment import Nature
from Play.weapons import *

pygame.init()
clock = pygame.time.Clock()
e = Nature()




def redraw_window():
    e.draw()
    e.move_background()
    e.win.blit(game_over, (e.width/4, e.high/3-position_y))

    pygame.display.update()


font_game_over = pygame.font.SysFont("comicsansms",40 )
font_game_over.set_bold( 15 )
game_over = font_game_over.render( 'GAME OVER', 1, (10, 128, 147) )
position_y =0
run = True
while run:

    pygame.time.delay(20)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        position_y+=1
    redraw_window()
clock.tick(100)
pygame.quit()