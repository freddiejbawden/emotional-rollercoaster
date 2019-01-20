import random
import math
import pygame
from collections import deque
import cv2
import time
import requests
from threading import Thread


vc = cv2.VideoCapture(0)

def take_pic():

    _, frame = vc.read()

    frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
    return frame_bytes

f_api = open("api_code.txt", "r")
api_key = f_api.readline()

q = 0
fire = 0
restart = 0
em = ""

def thread_fun(input=None):
    face(input)
    return

def face(frame_bytes):
    def pred_image(frame):
        headers = {'Ocp-Apim-Subscription-Key': api_key, 'Content-Type': 'application/octet-stream'}

        params = {
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'smile,emotion',
        }

        skip = 0
        response = requests.post(face_api_url, params=params, headers=headers, data=frame)
        jsonResponse = response.json()
        len(jsonResponse)
        if len(jsonResponse) == 0:
            skip = 1
            return 0, 0, skip
        else:
            return jsonResponse[0]["faceId"], jsonResponse[0]["faceAttributes"], skip

    face_api_url = 'https://westeurope.api.cognitive.microsoft.com/face/v1.0/detect'

    _, face_atts, skip = pred_image(frame_bytes)
    if (skip == 0):
        global q
        global fire
        global restart
        global em
        emotions = face_atts["emotion"]
        if (emotions["happiness"] < emotions["sadness"]):
            direction = -emotions["sadness"]
            q = direction
        else:
            direction = emotions["happiness"]
            q = direction
        if (emotions["anger"] > 0.04):
            shoot = 1
            fire=shoot
        else:
            shoot = 0
            fire=shoot

        if (emotions["surprise"] > 0.3):
            restart = 1
        else:
            restart = 0

        max_emot_val =  0
        for emot in emotions:
            if emotions[emot]>max_emot_val:
                max_emot_val = emotions[emot]
                max_emot = emot
        em = max_emot

my_thread = Thread(target=thread_fun)



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
gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('A bit Racey')

black = (0, 0, 0)
white = (255, 255, 255)

rollercoaster_history = deque(MAX_LENGTH * [(0, 0)], MAX_LENGTH)
terrain_history_top = deque(int(display_width / TERRAIN_WIDTH) * [(0, 0, 0, 0)], int(display_width / TERRAIN_WIDTH))
terrain_history_bottom = deque(int(display_width / TERRAIN_WIDTH) * [(0, 0, 0, 0)], int(display_width / TERRAIN_WIDTH))
clock = pygame.time.Clock()
crashed = False
carImg = pygame.image.load('rollercoaster.png')
carImg = pygame.transform.scale(carImg, (64, 22))
enemies = []

play_game = True


class Baddie:
    def __init__(self, x, y):
        self.img = pygame.image.load('baddie.png')
        self.x = x
        self.y = y
        self.speed = 3

    def moveBaddie(self):
        self.x -= self.speed
        gameDisplay.blit(self.img, (self.x, self.y))


class Car:
    def __init__(self, x, y):
        self.img = pygame.image.load('rollercoaster.png')
        self.img = pygame.transform.scale(self.img, (64, 22))
        self.x = x
        self.y = y
        self.max_velocity = 3;
        self.velocity = 0;

    def applyForce(self, force):
        self.velocity = force
        self.y += self.velocity
        gameDisplay.blit(self.img, (self.x, self.y))

    def get_terrain_slice(self):
        idx = int(self.x / TERRAIN_WIDTH - 1)
        return idx

    def test_collision(self, enemies):
        for e in enemies:
            if e.x <= self.x and math.fabs(e.x - self.x) < 16:
                if math.fabs(e.y - self.y) < 16:
                    return True
        return False


class Bullet:
    def __init__(self, x, y):
        self.img = pygame.image.load('bullet.png')
        self.x = x
        self.y = y
        self.speed = 10

    def move_bullet(self):
        self.x += self.speed
        if (self.x > display_width):
            return False
        else:
            gameDisplay.blit(self.img, (self.x, self.y))
            return True

    def test_collision(self, baddie_list):
        hits = []
        for baddie in baddie_list:
            if self.x > baddie.x:
                if math.fabs(self.y - baddie.y) < 24:
                    hits.append(baddie)
        return hits


x = (display_width * 0.2)
y = (display_height * 0.5)
y_change = 0
car_speed = 0
time_until_next_enemy = 1000

car = Car(x, y)

while not crashed:
    if (not my_thread.is_alive()):
        fb = take_pic()
        my_thread = Thread(target=thread_fun, kwargs={'input': fb})
        my_thread.start()
        count = 0
    if (play_game):


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True

            ############################
        if (fire):
            bullets.append(Bullet(car.x, car.y))

        print(q)
        y_change = -q

        gameDisplay.fill(white)
        car.applyForce(y_change)
        if score<500:
            terrain_bias = 0.2
        elif score<1000:
            terrain_bias = 0.3
        elif score <1500:
            terrain_bias = 0.35
        elif score >2000:
            terrain_bias = 0.4
        # Terrain Generation
        if (terrain_top_goal == terrain_top_current):
            terrain_top_goal = random.randint(1, display_width * terrain_bias)
        else:
            if (terrain_top_goal > terrain_top_current):
                terrain_top_current += terrain_delta
            else:
                terrain_top_current -= terrain_delta
        terrain_history_top.append((display_width, 0, TERRAIN_WIDTH, terrain_top_current))
        for i, r in enumerate(terrain_history_top):
            terrain_history_top[i] = pygame.Rect(r[0] - 20, r[1], r[2], r[3])
        for r in terrain_history_top:
            pygame.draw.rect(gameDisplay, pygame.Color(255, 0, 0, 255), r)

        # Terrain Generation Bottom
        if (terrain_bottom_goal == terrain_bottom_current):
            terrain_bottom_goal = random.randint(1, int(display_width * (terrain_bias+0.01)))
        else:
            if (terrain_bottom_goal > terrain_bottom_current):
                terrain_bottom_current += terrain_delta
            else:
                terrain_bottom_current -= terrain_delta

        terrain_history_bottom.append(
            (display_width, display_height - terrain_bottom_current, TERRAIN_WIDTH, terrain_bottom_current))
        for i, r in enumerate(terrain_history_bottom):
            terrain_history_bottom[i] = pygame.Rect(r[0] - 20, r[1], r[2], r[3])
        for r in terrain_history_bottom:
            pygame.draw.rect(gameDisplay, pygame.Color(255, 0, 0, 255), r)

        # move bullets
        for b in bullets:
            b.move_bullet()
        if (car.y < terrain_history_top[car.get_terrain_slice()][3]):
            print("finish")
            play_game = False
        elif (car.y > terrain_history_bottom[car.get_terrain_slice()][1] and
                      terrain_history_bottom[car.get_terrain_slice()][1] != 0):
            print("finish")
            play_game = False
        # score text
        if (car.test_collision(enemies)):
            play_game = False
        score += 1
        scoretext = myfont.render("Score {0}".format(score), 1, (0, 0, 0))
        gameDisplay.blit(scoretext, (5, 10))

        em_text = myfont.render("Current Emotion: {}".format(em), 1, (0, 0, 0))
        gameDisplay.blit(em_text, (5, display_height-40))

        if time_until_next_enemy < 0:
            print("enemy time!")
            enemies.append(Baddie(display_width - 50, display_height / 2))
            time_until_next_enemy = random.randint(3, 10) * 1000
        else:
            time_until_next_enemy -= clock.get_time()
        for e in enemies:
            e.moveBaddie()
            if e.x < -20:
                enemies.remove(e)

                # move bullets
        for b in bullets:
            b.move_bullet()
            if b.x > display_width:
                bullets.remove(b)
                continue
            hits = b.test_collision(enemies)
            if (len(hits) > 0):
                for h in hits:
                    enemies.remove(h)
                    bullets.remove(b)

        pygame.display.update()
        clock.tick(60)
    else:
        gameDisplay.fill(white)
        scoretext = myfont.render("You scored {}. Look surprised to restart.".format(score), 1, (0, 0, 0))
        gameDisplay.blit(scoretext, (5, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True

        if (restart):
            play_game = True
            score = 0
            x = (display_width * 0.2)
            y = (display_height * 0.5)
            y_change = 0
            car_speed = 0
            enemies = []
            bullets = []
            rollercoaster_history = deque(MAX_LENGTH * [(0, 0)], MAX_LENGTH)
            terrain_history_top = deque(int(display_width / TERRAIN_WIDTH) * [(0, 0, 0, 0)],
                                        int(display_width / TERRAIN_WIDTH))
            terrain_history_bottom = deque(int(display_width / TERRAIN_WIDTH) * [(0, 0, 0, 0)],
                                           int(display_width / TERRAIN_WIDTH))

            terrain_bias = 0.2

            car = Car(x, y)
            pygame.display.update()
        pygame.display.update()

pygame.quit()
quit()