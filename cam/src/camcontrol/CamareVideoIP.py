import cv2
import imutils
import os
from django.conf import settings

face_detection = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_frontalface_default.xml'))

class VideoIP(object):

    def __init__(self):
        self.cap = cv2.VideoCapture("rtsp://admin:Mumbai@123@203.192.228.175:554/")
        #self.cap = cv2.VideoCapture('rtsp://admin:123456@192.168.1.216/H264?ch=1&subtype=0')
        #cv2.VideoCapture('rtsp://username:password@192.168.1.64/1')

    def __del__(self):
        self.cap.release()

    def getFrameIP(self):
        success,imgNp = self.cap.read()
        resize = cv2.resize(imgNp, (640, 480), interpolation = cv2.INTER_LINEAR)
        ret, jpeg = cv2.imencode('.jpg', resize)
        return jpeg.tobytes()

    def getFrame(self):
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()
        success, frame = self.cap.read()
       #frame = imutils.resize(frame,width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_detected = face_detection.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors=5)
        for (x, y, w, h) in faces_detected:
            cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
        frame_flip = cv2.flip(frame,1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()
    
class VideoIPCredential(object):
    
    def __init__(self,user,password,urlIP):
        self.user = user
        self.password = password
        self.urlIP = urlIP
        self.cap = cv2.VideoCapture("rtsp://%s:%s@%s" % (user,password,urlIP))

    def __del__(self):
        self.cap.release()

    def getFrameIP(self):
        success,imgNp = self.cap.read()
        resize = cv2.resize(imgNp, (640, 480), interpolation = cv2.INTER_LINEAR)
        ret, jpeg = cv2.imencode('.jpg', resize)
        return jpeg.tobytes()

    def getFrame(self):
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()
        success, frame = self.cap.read()
        #frame = imutils.resize(frame,width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_detected = face_detection.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors=5)
        for (x, y, w, h) in faces_detected:
            cv2.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
        frame_flip = cv2.flip(frame,1)
        ret, jpeg = cv2.imencode('.jpg', frame_flip)
        return jpeg.tobytes()
    
class ListVideoIPCredential(object):
    global lista
    
    def __init__(self):
        global lista
        lista = []
        pass
    
    def addVideoIpCredential(videoip):
        global lista
        videoip = VideoIPCredential('admin','pass','192.168.1.216/H264?ch=1&subtype=0')
        lista.append(videoip)

    def showListVideoIP():
        global lista
        cont = 0
        while cont < len(lista):
            lista[cont]
            cont+=1
