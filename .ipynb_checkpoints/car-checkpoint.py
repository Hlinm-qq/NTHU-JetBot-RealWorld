from jetbot import Robot
import traitlets
import ipywidgets.widgets as widgets
from IPython.display import display
from jetbot import Camera, bgr8_to_jpeg
import os
import time
import cv2
import numpy as np

robot = Robot()

isLeft = False
isRight = False
isMiddle = False
isObstacle = False
left_cnt = 0
right_cnt = 0
obs_cnt = 0
cnt_stop = 0
frames = 0
isStop = False

LisBlack = False
LisWhite = False
RisBlack = False
RisWhite = False

lp = 160
rp = 489
spot = 260

def execute(change):
    
    ### forward <-> right, backward <-> left
    
    global robot, frames, isLeft, isRight,left_cnt, right_cnt, cnt_stop, isStop, LisBlack, LisWhite, RisBlack, RisWhite, lp, rp,spot, isMiddle,obs_cnt,isObstacle
    print("\rFrames", frames, end="")
    frames += 1
#     print(frames)

    # Visualize
    img_2 = cv2.resize(change["new"],(640,360))
    img = cv2.cvtColor(img_2, cv2.COLOR_RGB2GRAY)
#     cv2.imshow("camera", img)
#     cv2.imwrite('oxxostudio_3.png', img) 
#     print("ok")

    # initial run
    if frames == 1:
#         robot.stop()
        robot.right(0.15)
#         print(img[0][0])
#         print(img[0][639])
#         print(img[359][0])
#         print(img[359][639])

#     if frames == 1:
#         robot.stop()
#         for i in range(220, 420):
#             print((i, img_2[359][i]))
        
#         exit()
    if isStop:
        cnt_stop +=1
        print("cnt_stop")
        print(cnt_stop)
        if cnt_stop == 25:
            print("!!!!!!!!!")
            robot.stop()
            exit()

    if isLeft:
        left_cnt += 1

    if isRight:
        right_cnt += 1

    if isObstacle:
        obs_cnt += 1

    if left_cnt == 3:
        robot.right(0.15)
        isLeft = False
        left_cnt = 0

    if right_cnt == 3:
        robot.right(0.15)
        isRight = False
        right_cnt = 0
        
    if obs_cnt == 55:
        isObstacle = False
        obs_cnt = 0





    # check if (295, 270) ~ (345, 270) is RED ([38, 33, 172])
    if not (isLeft or isRight or isObstacle):
#         print("###")
#         print(img[359][320])
#         print("###")
        for j in range(50):
            if (img[359][295 + j] < 140):
                isMiddle = True
                break

        if not isMiddle:
            for i in range(100):
                if img[359][270 + i] < 140:
                    if i > 50:
                        print("Red is right, RIGHT TURN!")
                        robot.forward(0.1)
#                         robot.backward(0.15)
                        isLeft = True
                        break
                    else:
                        print("Red is left, LEFT TURN!")        
                        robot.backward(0.1)
#                         robot.forward(0.15)
                        isRight = True
                        break
        isMiddle = False

#         for x in range(170, 270):
#             if img[359][x] < 150:
#                 LisBlack = True
#             else:
#                 LisWhite = True
                
#         for x in range(370, 470):
#             if img[359][x] < 150:
#                 RisBlack = True
#             else:
#                 RisWhite = True
                
#         if (LisBlack and LisWhite) or (RisBlack and RisWhite):
#             robot.stop()
#         LisBlack = False
#         LisWhite = False
#         RisBlack = False
#         RisWhite = False
            
#         if( img[324][320][0] > 15 and img[324][320][0] < 45 and
    for k in range(220, 420):

        if( img_2[359][k][0] < 60 and
            img_2[359][k][1] < 80 and 
            img_2[359][k][2] < 110 and not isStop):
            print("stop")
            isStop = True
        
camera = Camera.instance(width=960, height=540, capture_width=1280, capture_height=720)
image = widgets.Image(format='jpeg', width=480, height=270)  # this width and height doesn't necessarily have to match the camera
camera_link = traitlets.dlink((camera, 'value'), (image, 'value'), transform=bgr8_to_jpeg)
# display(image)

execute({'new': camera.value})
camera.observe(execute, names='value')