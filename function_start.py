import cv2
import numpy as np
import os
import sys
import time
from face_reg import *
import queue
import PWMServo
from config import *


mode=-1
frame_copy=image=None
cap=''

def camera_open():
    global cap, mode

    try:
        if cap != '':
            try:
                cap.release()
            except Exception as e:
                print(e)
        cap = cv2.VideoCapture(-1)
        cap.set(12, 45)
        time.sleep(0.01)
        mode = 0
    except BaseException as e:
        print('open camera error:',e)

def camera_close():
    global cap, mode

    try:
        mode = -1
        time.sleep(0.1)
        cap.release()
        time.sleep(0.01)
    except BaseException as e:
        print('close camera error:', e)

def camera_task():  
    global image, frame_copy, debug, cap
    while True:
        if mode!=-1:
            try:
                ret, orgframe = cap.read()
                if ret:
                    frame_flip = cv2.flip(orgframe, 1)
                    frame_copy = frame_flip
                    if debug:
                        img_tmp = image if image is not None else frame_flip
                        cv2.imshow('image',img_tmp)
                        cv2.waitKey(1)
                    else:
                        img_tmp = image if image is not None else frame_flip

                    time.sleep(0.03)
                else:
                    cap=cv2.VideoCapture(-1)
                    time.sleep(0.01)

            except BaseException as e:
                print('主程序出错', e)
        else:
            time.sleep(0.01)

def face_tracker():
    global frame_copy, image
    global mode

    while True:
        if mode!=-1:
            if frame_copy is not None:
                image=face_track(frame_copy)
                frame_copy=None
                time.sleep(0.01)
            else:
                image=frame_copy
        else:
            time.sleep(0.01)

threading.Thread(target=face_tracker,daemon=True).start()
threading.Thread(target=camera_task,daemon=True).start()


if __name__=='__main__':
    camera_open()
    mode=0

    interrupt = False
    def signal_handle(signal, frame):
        global interrupt

        interrupt = True
        print('程序终止')

    while True:
        if interrupt:
            camera_close()
            break
        else:
            time.sleep(1)


