import pygame
import random
import math
from collections import deque

pygame.init()

MAX_LENGTH = 20
TERRAIN_WIDTH = 20
SPEED = 10

bullets = []

display_width = 800
display_height = 600

terrain_seed_top = 1
terrain_top_goal = 0
terrain_top_current = 0

terrain_seed_bottom = 3
terrain_bottom_goal = 0
terrain_bottom_current = 0

terrain_delta = 1

myfont = pygame.font.SysFont("monospace", 32)
score = 0
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A bit Racey')

black = (0,0,0)
white = (255,255,255)

rollercoaster_history = deque(MAX_LENGTH*[(0,0)], MAX_LENGTH)
terrain_history_top = deque(display_width/TERRAIN_WIDTH*[(0,0,0,0)], display_width/TERRAIN_WIDTH)
terrain_history_bottom = deque(display_width/TERRAIN_WIDTH*[(0,0,0,0)], display_width/TERRAIN_WIDTH)
clock = pygame.time.Clock()
crashed = False
carImg = pygame.image.load('rollercoaster.png')
carImg = pygame.transform.scale(carImg, (64,22))

play_game = True

class Baddie:
    def __init__(self,x,y):
        self.img = pygame.image.load('baddie.png')
        self.x = x
        self.y = y
        self.speed = 3
    def moveBaddie(self):
        self.x -= self.speed
        gameDisplay.blit(self.img, (self.x,self.y))


class Car:
    def __init__(self,x,y):
        self.img = pygame.image.load('rollercoaster.png')
        self.img = pygame.transform.scale(self.img, (64,22))
        self.x = x
        self.y = y
        self.max_velocity = 3;
        self.velocity = 0;
    def applyForce(self,force):
        if (math.fabs(self.velocity + force) < self.max_velocity):
            self.velocity += force
        self.y += self.velocity
        gameDisplay.blit(self.img, (self.x,self.y))
    def get_terrain_slice(self):
        idx = int(self.x/TERRAIN_WIDTH - 1)
        return idx


class Bullet:
    def __init__(self,x,y):
        self.img = pygame.image.load('bullet.png')
        self.x = x
        self.y = y
        self.speed = 10
    def move_bullet(self):
        self.x += self.speed
        if (self.x > display_width):
            return False
        else:
            gameDisplay.blit(self.img, (self.x,self.y))
            return True
    def test_collision(self, baddie_list):
        hits = []
        for baddie in baddie_list:
            if self.x > baddie.x:
                if math.fabs(self.y - baddie.y) < 16:
                    hits.append(baddie)
        return hits



x =  (display_width * 0.2)
y = (display_height * 0.5)
y_change = 0
car_speed = 0

car = Car(x,y)


while not crashed:
    if (play_game):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True

            ############################
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    y_change = -0.1
                elif event.key == pygame.K_DOWN:
                    y_change = 0.1
                elif event.key == pygame.K_SPACE:
                    bullets.append(Bullet(car.x,car.y))
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    y_change = 0

        gameDisplay.fill(white)
        car.applyForce(y_change)
    


        # Terrain Generation
        if (terrain_top_goal == terrain_top_current):
            terrain_top_goal = random.randint(1, display_width*0.2)
        else:
            if (terrain_top_goal > terrain_top_current):
                terrain_top_current += terrain_delta
            else:
                terrain_top_current -= terrain_delta
        terrain_history_top.append((display_width,0,TERRAIN_WIDTH,terrain_top_current))
        for i,r in enumerate(terrain_history_top):
            terrain_history_top[i] = pygame.Rect(r[0]-20,r[1],r[2],r[3])
        for r in terrain_history_top:
            pygame.draw.rect(gameDisplay,pygame.Color(255, 0, 0, 255),r)

        # Terrain Generation Bottom
        if (terrain_bottom_goal == terrain_bottom_current):
            terrain_bottom_goal = random.randint(1, display_width*0.3)
        else:
            if (terrain_bottom_goal > terrain_bottom_current):
                terrain_bottom_current += terrain_delta
            else:
                terrain_bottom_current -= terrain_delta

        terrain_history_bottom.append((display_width,display_height-terrain_bottom_current,TERRAIN_WIDTH,terrain_bottom_current))
        for i,r in enumerate(terrain_history_bottom):
            terrain_history_bottom[i] = pygame.Rect(r[0]-20,r[1],r[2],r[3])
        for r in terrain_history_bottom:
            pygame.draw.rect(gameDisplay,pygame.Color(255, 0, 0, 255),r)

        #move bullets
        for b in bullets:
            b.move_bullet()
        print(car.y, terrain_history_top[car.get_terrain_slice()][3])
        if (car.y < terrain_history_top[car.get_terrain_slice()][3]):
            print("finish")
            play_game = False
        elif (car.y > terrain_history_bottom[car.get_terrain_slice()][1] and terrain_history_bottom[car.get_terrain_slice()][1] != 0):
            print("finish")
            play_game = False
        #score text
        score += 1
        scoretext = myfont.render("Score {0}".format(score), 1, (0,0,0))
        gameDisplay.blit(scoretext, (5, 10))
        pygame.display.update()
        clock.tick(60)
    else:
        gameDisplay.fill(white)
        scoretext = myfont.render("You scored {}. Press R to restart.".format(score), 1, (0,0,0))
        gameDisplay.blit(scoretext, (5, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    play_game = True
                    score = 0
                    x =  (display_width * 0.2)
                    y = (display_height * 0.5)
                    y_change = 0
                    car_speed = 0

                    car = Car(x,y)
        pygame.display.update()



pygame.quit()
quit()
