import cv2
from django.conf import settings
import numpy as np
import datetime
from cam.src.utils.ConversionFechas import  segundos_a_segundos_minutos_y_horas


class ShowVideo(object):
    
    def __init__(self):
        self.cap = None
        self.velocidad = 20
        self.numeroFrames = 0
        self.start = True
        self.totSegundos = 0

    def __del__(self):
        if self.cap!=None:
            self.cap.release()
        cv2.destroyAllWindows()

    def getVelocidad(self):
        return self.velocidad
    def getNumeroFrames(self):
        return self.numeroFrames
    def getTotSegundos(self):
        return  self.totSegundos

    def getVideo(self,pathFile,option,numeroFrames,velocidad):
        self.cap = cv2.VideoCapture(str(pathFile))
        timeToshow = None
        fontFace = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        fontlineType = cv2.LINE_4
        fontColor = (255,0,0)
        self.totSegundos = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS))
        tiempoVideo = segundos_a_segundos_minutos_y_horas(self.totSegundos)

        widthVideo  = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        heichtVideo = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        timeVideoX  = int(widthVideo - 1200)
        timeVideoY  = int(heichtVideo - 20)
        frameVideoX = int(widthVideo - 880)
        frameVideoY = int(heichtVideo - 20)

        if numeroFrames > 0 and (option == 2 or option == 3 or option == 4 or option == 5 or option == 6):
            print("numero FRame ",numeroFrames)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,numeroFrames)

        if option == 1:
            self.start = True
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,0)
        elif option == 2:
            self.start = True
        elif option == 3:
            self.start = False
        elif (option == 4 or option == 5):
            if (velocidad > 0 and velocidad < 200):
                self.velocidad = velocidad
            elif velocidad < 1 :
                self.velocidad = 1
            else:
                self.velocidad = 200
            print("velocidad",self.velocidad)

        print("--total de frames----",self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print("--total de FPS   ----",self.cap.get(cv2.CAP_PROP_FPS))


        while self.cap.isOpened():
            success, frame = self.cap.read()
            #timeToshow = datetime.datetime.fromtimestamp(self.cap.get(cv2.CAP_PROP_POS_MSEC)/1000.0)
            timeToshow = segundos_a_segundos_minutos_y_horas(int(self.cap.get(cv2.CAP_PROP_POS_MSEC)/1000))

            self.numeroFrames = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            if not success:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            
            cv2.putText(frame,str(timeToshow +"-"+tiempoVideo+","),(timeVideoX,timeVideoY),fontFace,fontScale,fontColor,fontlineType)
            #cv2.putText(frame,str(timeToshow.strftime(settings.DATE_INPUT_FORMATS[2])+"-"+tiempoVideo+","),(timeVideoX,timeVideoY),fontFace,fontScale,fontColor,fontlineType)
            #cv2.putText(frame,"Frame :"+str(self.numeroFrames),(frameVideoX,frameVideoY),fontFace,fontScale,fontColor,fontlineType)
            cv2.waitKey(self.velocidad)

            ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

            if not self.start:
                break
