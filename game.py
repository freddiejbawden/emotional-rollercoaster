import pygame
import asyncio
from collections import deque
import cv2
import time
import datetime
import requests
import csv

f_api = open("api_code.txt", "r")
api_key = f_api.readline()
def face():
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

    vc = cv2.VideoCapture(0)

    if vc.isOpened():  # try to get the first frame
        rval, frame = vc.read()
    else:
        rval = False


    rval, frame = vc.read()
    # key = cv2.waitKey(20)
    frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
    _, face_atts, skip = pred_image(frame_bytes)

    if (skip == 0):
        emotions = face_atts["emotion"]
        if (emotions["happiness"] < emotions["sadness"]):
            direction = -emotions["sadness"]
        else:
            direction = emotions["happiness"]
        if (emotions["anger"] > 0.08):
            shoot = True
            print("FIRE!")
        else:
            shoot = False

        print(direction)

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
count=0

while not crashed:
    count = count+1
    if count > 20:
        print("sdgasdg")
        face()
        count = 0
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