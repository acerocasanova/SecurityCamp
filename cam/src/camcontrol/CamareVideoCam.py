import cv2
import imutils
import os
import time
import numpy as np
from django.conf import settings

from cam.src.camcontrol.SharedCamera import SharedCamera
from cam.src.camcontrol.streaming import FrameStrategy, mjpeg_stream

face_detection  = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_frontalface_default.xml'))
sizeShowCam = 500
scale_Factor = 1.3
min_Neighbors = 5


class _LiveFlipStrategy(FrameStrategy):
    """
    Espeja el frame (igual que FlipStrategy) y ademas deja una copia en
    las variables de modulo success/frame_flip/gray. Eso es lo que le
    permite a takeAPicture() -llamado desde OTRA request, cuando el
    usuario aprieta 'Tomar Foto' mientras esta viendo la camara en vivo-
    guardar exactamente el frame que se esta mostrando en ese momento.
    Es el unico motivo por el que esta estrategia no es simplemente la
    FlipStrategy generica de strategies.py.
    """

    def process(self, frame):
        global success, frame_flip, gray
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_flip = cv2.flip(frame, 1)
        success = True
        return frame_flip


class VideoCam(object):
    global success,frame,frame_flip,gray

    def __init__(self):
        self.cap = SharedCamera.get_camera(0)
        self.dirRecordPath = os.listdir(settings.STORAGE_CAM_RECORD)

    def __del__(self):
        self.cap.release()

    def stream(self):
        """Vista en vivo de la webcam local (home / tomar foto de un
        registro). Antes tenia su propio while+encode+yield (getVideo());
        ahora es el template mjpeg_stream() + la estrategia de espejado."""
        return mjpeg_stream(self.cap, [_LiveFlipStrategy()])

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
