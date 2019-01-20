import pygame
from collections import deque

pygame.init()
MAX_LENGTH = 20
display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')

black = (0,0,0)
white = (255,255,255)
rollercoaster_history = deque(MAX_LENGTH*[(0,0)], MAX_LENGTH)
clock = pygame.time.Clock()
crashed = False
carImg = pygame.image.load('rollercoaster.png')
carImg = pygame.transform.scale(carImg, (64,64))



def car(x,y):
    gameDisplay.blit(carImg, (x,y))

x =  (display_width * 0.2)
y = (display_height * 0.8)
y_change = 0
car_speed = 0

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

        ############################
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                y_change = -5
            elif event.key == pygame.K_DOWN:
                y_change = 5
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                y_change = 0
        ######################
    ##
    y += y_change
   ##
    gameDisplay.fill(white)
    car(x,y)
    rollercoaster_history.appendleft((x,y))
    for i,(t_x, t_y) in enumerate(rollercoaster_history):
        rollercoaster_history[i] = (t_x - 10, t_y)
    if (len(rollercoaster_history) == MAX_LENGTH):
        pygame.draw.lines(gameDisplay, pygame.Color(255, 0, 0, 255),False,rollercoaster_history)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()
