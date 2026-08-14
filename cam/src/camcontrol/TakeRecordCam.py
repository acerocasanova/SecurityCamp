import cv2
import os, shutil
import time
import numpy as np
from django.conf import settings

class TakeRecordCam(object):
    global frame,frame_flip

    def __init__(self):
        self.face_detection  = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_frontalface_default.xml'))
        self.side_face_detection = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_profileface.xml'))

        self.cap = cv2.VideoCapture(0)
        createDirectory = os.path.join(settings.STORAGE_CAM_RECORD)
        if not  os.path.exists(createDirectory):
            os.makedirs(settings.STORAGE_CAM_RECORD)

        createDirectory = os.path.join(settings.DIR_CONFIG_FILES)
        if not  os.path.exists(createDirectory):
            os.makedirs(settings.DIR_CONFIG_FILES)

        self.dirRecordPath = os.listdir(settings.STORAGE_CAM_RECORD)

    def __del__(self):
        self.cap.release()

    def getMODELOEIGENFACE(self):
        self.face_recognizer = cv2.face.EigenFaceRecognizer_create()
        self.face_recognizer.read(os.path.join(settings.DIR_CONFIG_FILES, settings.MODELOEIGENFACE))

    def getMODELOFISHERFACE(self):
        self.face_recognizer = cv2.face.FisherFaceRecognizer_create()
        self.face_recognizer.read(os.path.join(settings.DIR_CONFIG_FILES,settings.MODELOFISHERFACE))

    def getMODELOLBPHFACE(self):
        #if not os.path.isfile(os.path.join(settings.DIR_CONFIG_FILES, settings.MODELOLBPHFACE)):
        #    createFile = open(os.path.join(settings.DIR_CONFIG_FILES,settings.MODELOLBPHFACE), "w")
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_recognizer.read(os.path.join(settings.DIR_CONFIG_FILES,settings.MODELOLBPHFACE))

    def createProgressBar(self,percentage,mensaje = 'procesando', width = 700):
        global frame,frame_flip
        filled_length = int((width * percentage) / 100)
        color =(0,255,0)
        cv2.rectangle(frame_flip,(0,0),(filled_length,50),color, -1)
        font = 1
        text = "{}% {}".format(percentage,mensaje)
        text_size,_ = cv2.getTextSize(text,font,1,2)[0]
        text_x = (width - text_size) // 2
        cv2.putText(frame_flip,text,(10,38),font,3,(255,0,0),3)

    def genRecord(self,showRecord):
        global frame,frame_flip
        count = 1
        countAux = 0
        progress = 1
        countMax = 300
        color = (255,0,0)
        thickness=2
        #execThread = True
        #result = 0
        #resultAux = 0
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()
        #trheadTrainREcord =  threading.Thread(target=self.trainRecord)
        while self.cap.isOpened():
            success, frame = self.cap.read()
            gray  = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            sideGray = cv2.flip(gray,1)

            if success:
                if count <= countMax:
                    savePath = os.path.join(settings.STORAGE_CAM_RECORD,showRecord.image_name)
                    if not  os.path.exists(savePath):
                        os.makedirs(savePath)
                    auxFrame = frame.copy()
                    faces = self.face_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                    sideFace     = self.side_face_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                    othersideFace= self.side_face_detection.detectMultiScale(sideGray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)

                    for (x,y,w,h) in faces: #si se detecta un rostro se almacenara en estas variables
                        cv2.rectangle(frame,pt1=(x,y),pt2=(x+w,y+h),color=color,thickness=thickness)
                        rostro = auxFrame[y:y+h,x:x+w]
                        try:
                            rostro = cv2.resize(rostro,(150,150),interpolation = cv2.INTER_CUBIC)
                            cv2.imwrite("{}/{}_{}{}".format(savePath,showRecord.image_name,count,settings.EXTENSION_IMG),rostro)
                        except Exception as e:
                            print("Warning! Error al capturar una imagen ",str(e))
                        count = count + 1

                    for (x,y,w,h) in sideFace:
                        cv2.rectangle(frame,pt1=(x,y),pt2=(x+w,y+h),color=color,thickness=thickness)
                        rostro = auxFrame[y:y+h,x:x+w]
                        try:
                            rostro = cv2.resize(rostro,(150,150),interpolation = cv2.INTER_CUBIC)
                            cv2.imwrite("{}/{}_{}{}".format(savePath,showRecord.image_name,count,settings.EXTENSION_IMG),rostro)
                        except Exception as e:
                            print("Warning! Error al capturar una imagen ",str(e))
                        count = count + 1

                    frame_flip = cv2.flip(frame,1)
                    for (x,y,w,h) in othersideFace:
                        cv2.rectangle(frame_flip,pt1=(x,y),pt2=(x+w,y+h),color=color,thickness=thickness)
                        rostro = auxFrame[y:y+h,x:x+w]
                        try:
                            rostro = cv2.resize(rostro,(150,150),interpolation = cv2.INTER_CUBIC)
                            cv2.imwrite("{}/{}_{}{}".format(savePath,showRecord.image_name,count,settings.EXTENSION_IMG),rostro)
                        except Exception as e:
                            print("Warning! Error al capturar una imagen ",str(e))
                        count = count + 1

                    if  count % 3 == 0 and count != countAux:
                        progress += 1
                        countAux = count
                        self.createProgressBar(progress,mensaje='proceso 1 de 1')
                    else:
                        self.createProgressBar(progress,mensaje='proceso 1 de 1')

                    ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame_flip)
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
                else:
                    frame_flip = cv2.flip(frame,1)
                    self.createProgressBar(100,mensaje='proceso Finalizado')
                    #if execThread:
                    #    execThread = False
                    #    trheadTrainREcord.start()
                    ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame_flip)
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def getVideoEIGENFACE(self):
        if not self.cap.isOpened():
            print("No se puede acceder a la camara")
            exit()
        self.getMODELOEIGENFACE()
        while self.cap.isOpened:
            success, frame = self.cap.read()
            gray  = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            if success:
                auxFrame = gray.copy()
                faces = self.face_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                frame_flip = cv2.flip(frame,1)
                for (x,y,w,h) in faces:
                    rostro = auxFrame[y:y+h,x:x+w]
                    rostro = cv2.resize(rostro,(150,150),interpolation = cv2.INTER_CUBIC)#tiene que tener el mismo tamaño de imagene QUE EN EL RECONOCIMIENTO
                    result = self.face_recognizer.predict(rostro)#predice una etiqueta y una confianza determinada
                    #cv2.putText(frame_flip,'{}'.format(result),(x,y-5),1,1.3,(255,255,0),1,cv2.LINE_AA)

                    if result[1] < 5700 :
                        #cv2.putText(frame_flip,'{}'.format(self.dirRecordPath[result[0]]),(x,y-25),1,3,(255,0,0),3,cv2.LINE_AA)

                        try:
                            showDate = self.dirRecordPath[result[0]].split("_")
                            #print("mostrando = ", showDate[0])
                            cv2.putText(frame_flip,showDate[0],(x,y-150),1,3,(255,0,0),3,cv2.LINE_AA)
                            cv2.putText(frame_flip,showDate[1],(x,y-100),1,3,(255,0,0),3,cv2.LINE_AA)
                            cv2.putText(frame_flip,showDate[2],(x,y-50),1,3,(255,0,0),3,cv2.LINE_AA)
                        except:
                            pass

                        #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,2555,0),2)
                    else:
                        cv2.putText(frame_flip,'Desconocido',(x,y-20),2,3,(0,0,255),3,cv2.LINE_AA)
                        #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

                ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame_flip)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def getVideoLBPH(self):
        if not self.cap.isOpened():
            print("No se puede acceder a la camara")
            exit()
        self.getMODELOLBPHFACE()

        while self.cap.isOpened:
            success, frame = self.cap.read()
            gray  = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            if success:
                auxFrame = gray.copy()
                faces = self.face_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                frame_flip = cv2.flip(frame,1)
                for (x,y,w,h) in faces:
                    rostro = auxFrame[y:y+h,x:x+w]
                    rostro = cv2.resize(rostro,(150,150),interpolation = cv2.INTER_CUBIC)#tiene que tener el mismo tamaño de imagene QUE EN EL RECONOCIMIENTO
                    result = self.face_recognizer.predict(rostro)#predice una etiqueta y una confianza determinada
                    #print("numero representado ",result[1])
                    if result[1] < 90 :
                        #showDate = self.dirRecordPath[result[0]].replace("_", "\n")

                        try:
                            showDate = self.dirRecordPath[result[0]].split("_")
                            #print("mostrando = ", showDate[0])
                            cv2.putText(frame_flip,showDate[0],(x,y-150),1,3,(255,0,0),3,cv2.LINE_AA)
                            cv2.putText(frame_flip,showDate[1],(x,y-100),1,3,(255,0,0),3,cv2.LINE_AA)
                            cv2.putText(frame_flip,showDate[2],(x,y-50),1,3,(255,0,0),3,cv2.LINE_AA)
                        except:
                            pass
                        #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,2555,0),2)
                    else:
                        cv2.putText(frame_flip,'Desconocido',(x,y-20),2,0.8,(0,0,255),3,cv2.LINE_AA)
                        #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

                ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame_flip)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def getVideoFISHERFACE(self):
        if not self.cap.isOpened():
            print("No se puede acceder a la camara")
            exit()
        self.getMODELOFISHERFACE()

        while self.cap.isOpened:
            success, frame = self.cap.read()
            gray  = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            if success:
                auxFrame = gray.copy()
                faces = self.face_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                for (x,y,w,h) in faces:
                    rostro = auxFrame[y:y+h,x:x+w]
                    rostro = cv2.resize(rostro,(150,150),interpolation = cv2.INTER_CUBIC)#tiene que tener el mismo tamaño de imagene QUE EN EL RECONOCIMIENTO
                    result = self.face_recognizer.predict(rostro)#predice una etiqueta y una confianza determinada
                    print("numero representado ",result[1])
                    if result[1] < 500 :

                        try:
                            showDate = self.dirRecordPath[result[0]].split("_")
                            cv2.putText(frame,showDate[0],(x,y-150),1,3,(255,0,0),3,cv2.LINE_AA)
                            cv2.putText(frame,showDate[1],(x,y-100),1,3,(255,0,0),3,cv2.LINE_AA)
                            cv2.putText(frame,showDate[2],(x,y-50),1,3,(255,0,0),3,cv2.LINE_AA)
                        except:
                            pass
                        #cv2.putText(frame,'{}'.format(self.dirRecordPath[result[0]]),(x,y-25),1,3,(255,0,0),3,cv2.LINE_AA)
                        #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,2555,0),2)
                    else:
                        cv2.putText(frame,'Desconocido',(x,y-20),2,0.8,(0,0,255),3,cv2.LINE_AA)
                        #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

                frame_flip = cv2.flip(frame,1)
                ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def trainRecord(self):
        labels = []
        faceData = []
        label = 0
        #print("0 ",self.dirRecordPath)
        for nameDir  in self.dirRecordPath:
            personPath = str(settings.STORAGE_CAM_RECORD) + '/' + nameDir
            print("nombre persona ",personPath)
            for fileName in os.listdir(personPath):
                labels.append(label)
                faceData.append(cv2.imread(personPath+'/'+fileName,0))
            label = label + 1
        face_recognizer = cv2.face.EigenFaceRecognizer_create()
        print("cargando entrenamiento")
        inicioTiemo = time.time()
        face_recognizer.train(faceData,np.array(labels))
        tiempoEntrenamiento = time.time() - inicioTiemo
        print("tiempo de demora ",tiempoEntrenamiento)
        face_recognizer.write(os.path.join(settings.DIR_CONFIG_FILES, settings.MODELOEIGENFACE))
        print("fin cargado y entrenado")

    def deleteRecord(self,showRecord):
        path_delete = os.path.join(settings.STORAGE_CAM_RECORD,showRecord.image_name)
        try:
            if os.path.exists(path_delete):
                shutil.rmtree(path_delete)
        except Exception as e:
            print("Warning! Error ",str(e))
