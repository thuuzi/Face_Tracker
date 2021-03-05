import cv2
import sys
import os
import time
import numpy as np
import queue
import threading
import gc
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
import math
import datetime
import smtplib
import re
import dlib
import pid
import PWMServo
from config import *

#part 0:preparation

def leMap(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#找出面积最大的轮廓
#参数为要比较的轮廓的列表
def getAreaMaxContour(contours) :
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None;

        for c in contours : #历遍所有轮廓
            contour_area_temp = math.fabs(cv2.contourArea(c)) #计算轮廓面积
            if contour_area_temp > contour_area_max :
                contour_area_max = contour_area_temp
                if contour_area_temp > 64:  #只有在面积大于8时，最大面积的轮廓才是有效的，以过滤干扰
                    area_max_contour = c

        return area_max_contour, contour_area_max#返回最大的轮廓


servo1_face_track = 1200
servo2_face_track = 1500
dis_ok_face = False
action_finish_face = True

servo1_pid3 = pid.PID(P=1.0, I=0.5, D=0.01)
servo2_pid4 = pid.PID(P=0.8, I=0.5, D=0.01)

#part 1:face recognition


if DNN == "CAFFE":
    modelFile = "/home/pi/VisionPi/models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
    configFile = "/home/pi/VisionPi/models/deploy.prototxt"
    net = cv2.dnn.readNetFromCaffe(configFile, modelFile)
else:
    modelFile = "/home/pi/VisionPi/models/opencv_face_detector_uint8.pb"
    configFile = "/home/pi/VisionPi/models/opencv_face_detector.pbtxt"
    net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)


count = 0

import face_recognition
def detectFaceOpenCVDnn(frame):
    global net
    global count

    frameOpencvDnn = frame
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 2, (150,150), [104, 117, 123], False, False)
    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            count += 1
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
    if count >= 5:
        count = 0

    gc.collect()
    return frameOpencvDnn, 'detect_ok'

#part 2:face track

def track():
    global servo1_face_track, servo2_face_track
    global dis_ok_face, action_finish_face

    while True:
    #云台跟踪
        if dis_ok_face:
            dis_ok_face = False
            action_finish_face = False
            PWMServo.setServo(1, servo1_face_track, 20)
            PWMServo.setServo(2, servo2_face_track, 20)
            time.sleep(0.02)
            action_finish_face = True
        else:
            time.sleep(0.01)


cv_color_track = threading.Thread(target=track)
cv_color_track.setDaemon(True)
cv_color_track.start()

def face_track(frame):
    global servo1_face_track, servo2_face_track
    global dis_ok_face, action_finish_face
    global servo1_pid3, servo2_pid4
    global net

    img_tmp = None
    image = frame
    frameOpencvDnn = cv2.resize(frame,(160 , 120), interpolation = cv2.INTER_CUBIC)

    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]

    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1, (150, 150), [104, 117, 123], False, False)
    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    max_area = 0 #最大的人脸的box面积
    max_face = (0,0,0,0) #最大的人脸的box
    
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.35: #人脸检测阈值
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            area_tmp = ((y2 - y1 + 1) * (x2 - x1 + 1))
            if max_area < area_tmp: #对比，判断是否时最大的人脸
                max_area = area_tmp
                max_face = (x1, y1, x2, y2)
            rx1 = int(leMap(x1, 0,160, 0, 640)) #将坐标转换为 640 * 480
            ry1 = int(leMap(y1, 0,120, 0, 480))
            rx2 = int(leMap(x2, 0,160, 0, 640))
            ry2 = int(leMap(y2, 0,120, 0, 480))
            cv2.rectangle(frame, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2) 

    img_center_y = 60 
    img_center_x = 80
    if max_area != 0: 
        center_x, center_y = (max_face[0] + int((max_face[2] - max_face[0]) / 2), max_face[1] + int((max_face[3] - max_face[1]) /2)) 
        

        servo1_pid3.SetPoint = center_y if abs(img_center_y - center_y) < 20 else img_center_y 
        servo1_pid3.update(center_y)
        tmp = int(servo1_face_track - servo1_pid3.output)
        tmp = tmp if tmp > 500 else 500
        servo1_face_track = tmp if tmp < 1950 else 1950 


        servo2_pid4.SetPoint = center_x if abs(img_center_x - center_x) < 40 else img_center_x 
        servo2_pid4.update(2 * img_center_x - center_x)
        tmp = int(servo2_face_track + servo2_pid4.output)
        tmp = tmp if tmp > 500 else 500
        servo2_face_track = tmp if tmp < 2500 else 2500 #舵机角度限位
        if action_finish_face:
            dis_ok_face = True
    
    gc.collect()
    return image

