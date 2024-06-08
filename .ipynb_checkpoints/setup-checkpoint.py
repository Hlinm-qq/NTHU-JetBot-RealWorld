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
isObstacle = False
left_cnt = 0
right_cnt = 0
obs_cnt = 0
cnt_stop = 0
frames = 0
isStop = False

lp = 160
rp = 489
spot = 260

def execute(change):
    
    ### forward <-> right, backward <-> left
    
    global robot, frames, isLeft, isRight,left_cnt, right_cnt,cnt_stop, isStop, isObstacle, obs_cnt, lp, rp,spot
    print("\rFrames", frames, end="")
    frames += 1
#     print(frames)

    # Visualize
    img = cv2.resize(change["new"],(640,360))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
#     cv2.imshow("camera", img)
    cv2.imwrite('oxxostudio_3.png', img) 
#     print("ok")

    # initial run
#     if frames == 1:
# #         robot.stop()
#         robot.right(0.1)
#         print(img[0][0])
#         print(img[0][639])
#         print(img[359][0])
#         print(img[359][639])

    if frames == 1:
#         cv2.imshow("camera", img)
        for i in range(640):
            print((i, img [359][i]))
        cv2.waitKey(0)
    # if frames == 2700:
    #     cv2.imshow("camera", img)
    #     for i in range(640):
    #         print((i, img [180][i]))
    #     cv2.waitKey(0)
        # cv2.destroyAllWindows()
    if isStop:
        cnt_stop +=1
        if cnt_stop == 70:
            robot.stop()

    if isLeft:
        left_cnt += 1

    if isRight:
        right_cnt += 1

    if isObstacle:
        obs_cnt += 1

    if left_cnt == 5:
        robot.right(0.1)
        isLeft = False
        left_cnt = 0

    if right_cnt == 5:
        robot.right(0.1)
        isRight = False
        right_cnt = 0
        
    if obs_cnt == 55:
        isObstacle = False
        obs_cnt = 0





    # check if (295, 270) ~ (345, 270) is RED ([38, 33, 172])
    if not (isLeft or isRight or isObstacle):
            
#         if img[spot][lp][0] > 175 and img[spot][lp][0] < 210 and img[spot][lp][1] > 230 and img[spot][lp][1] < 260 and img[spot][lp][2] > 210 and img[spot][lp][2] < 260:#left obstacle
#             robot.forward(0.1)
#             isRight = True
#             isObstacle = True
#             print("R")
#             # robot.forward(0.05)
#         elif img[spot][rp][0] > 175 and img[spot][rp][0] < 210 and img[spot][rp][1] > 230 and img[spot][rp][1] < 260 and img[spot][rp][2] > 210 and img[spot][rp][2] < 260:#right obstacle
#             robot.backward(0.1)
#             isLeft = True
#             isObstacle = True
#             print("L")
#         elif img[spot][lp][0] > 100 and img[spot][lp][0] < 130 and img[spot][lp][1] > 120 and img[spot][lp][1] < 150 and img[spot][lp][2] > 105 and img[spot][lp][2] < 135:#left obstacle
#             robot.forward(0.1)
#             isRight = True
#             isObstacle = True
#             print("R")
#         elif img[spot][rp][0] > 100 and img[spot][rp][0] < 130 and img[spot][rp][1] > 120 and img[spot][rp][1] < 150 and img[spot][rp][2] > 105 and img[spot][rp][2] < 135:#right obstacle
#             robot.backward(0.1)
#             isLeft = True
#             isObstacle = True
#             print("L")
#         else:
        if not (img[324][320][0] < 10 and img[324][320][1] < 65 and img[324][320][1] > 45 and img[324][320][2] > 140):
            for i in range(640):
                if img[324][i][0] < 10 and img[324][i][1] < 65 and img[324][i][1] > 45 and img[324][i][2] > 140:
                    if i < 320:
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

    if img[324][320][0] > 15 and img[324][320][0] < 45 and img[324][320][1] > 30 and img[324][320][1] < 60 and img[324][320][2] < 100 and img[324][320][2] > 70:
        isStop = True
        
camera = Camera.instance(width=960, height=540, capture_width=1280, capture_height=720)
image = widgets.Image(format='jpeg', width=480, height=270)  # this width and height doesn't necessarily have to match the camera
camera_link = traitlets.dlink((camera, 'value'), (image, 'value'), transform=bgr8_to_jpeg)
# display(image)

execute({'new': camera.value})
camera.observe(execute, names='value')