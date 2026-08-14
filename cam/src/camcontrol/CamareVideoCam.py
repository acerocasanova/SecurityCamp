import cv2
import imutils
import os
import time
import numpy as np
from django.conf import settings

face_detection  = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_frontalface_default.xml'))
sizeShowCam = 500
scale_Factor = 1.3
min_Neighbors = 5

class VideoCam(object):
    global success,frame,frame_flip,gray
    
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.dirRecordPath = os.listdir(settings.STORAGE_CAM_RECORD)

    def __del__(self):
        self.cap.release()

    def getVideo(self):
        global success,frame,frame_flip,gray
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()
        success, frame = self.cap.read()
        #frame = imutils.resize(frame,width=500)
        gray  = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        frame_flip = cv2.flip(frame,1)
        ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame_flip)
        return jpeg.tobytes()

    def getFrame(self):
        global success,frame
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()
        success, frame = self.cap.read()
        #frame = imutils.resize(frame,width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_detected = face_detection.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors=5)
        for (x, y, w, h) in faces_detected:
            cv2.rectangle(frame,pt1=(x, y),pt2=(x + w, y + h),color=(255, 0, 0),thickness=2)
        frame_flip = cv2.flip(frame,1)
        ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame_flip)
        return jpeg.tobytes()

    def takeAPicture(self,showRecord):
        global frame_flip,success
        if success:
            cv2.imwrite(os.path.join(settings.STORAGE_RECORD,showRecord.image_name+settings.EXTENSION_IMG), frame_flip)

    def deleteAPicture(self,showRecord):
        try:
            os.remove(os.path.join(settings.STORAGE_RECORD,showRecord.image_name+settings.EXTENSION_IMG))
        except Exception as e:
            print("Warning! Error ",str(e))
