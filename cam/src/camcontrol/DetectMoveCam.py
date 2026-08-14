import cv2, os, time
import numpy as np
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from cam.tasks import send_msm_web_whatsapp
from cam.src.configuracion.Configuracion import DictonaryConfiguration, Web_whatsapp
from cam.src.configuracion.AgregarCamara import ConfiguracionAgregarCamara
import threading
from cam.src.camcontrol.TypeCam import GetTypeCam
from cam.models import Imagen
from cam.src.utils.WorksFiles import WorksFiles




class DetectMoveCam(object):
    
    def __init__(self,idCam):

        if idCam > 0:
            cam = ConfiguracionAgregarCamara()
            showCam = cam.get_find_cam(idCam)
            getTypeCam = GetTypeCam()
            
            if showCam.a_tipo_cam == 0:
                self.cap = cv2.VideoCapture(getTypeCam.get_cam_integrada(showCam))
            elif idCam != 0 and showCam.a_tipo_cam == 1:
                self.cap = cv2.VideoCapture(getTypeCam.get_cam_ip(showCam))
        else:
            self.cap = cv2.VideoCapture(0)


        self.full_body_detection   = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_fullbody.xml'))
        self.lower_body_detection  = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_lowerbody.xml'))
        self.upper_body_detection  = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_upperbody.xml'))
        self.face_detection        = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_frontalface_default.xml'))
        self.eyes_detection        = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_eye.xml'))
        self.side_face_detection   = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_profileface.xml'))
        
        self.dirRecordPath = os.listdir(settings.STORAGE_MOVE_DETECTED)

        config = DictonaryConfiguration()
        
    
        self.number_whatsapp = config.find_config(Web_whatsapp.NUMERO_WEBWHATSAPP,Web_whatsapp.NUMERO_WEBWHATSAPP_OMISION)
        self.between_seconds = config.find_config(Web_whatsapp.TIEMPO_ENTREME_MSM,Web_whatsapp.NUMERO_WEBWHATSAPP_OMISION)
        
        if self.number_whatsapp > 0:
            self.control_seconds = timedelta(seconds=60)
            for find_val in self.between_seconds:
                self.control_seconds = timedelta(seconds=find_val[0])

            self.controlTime = datetime.now()
            self.controlTimeAux = self.controlTime - self.control_seconds

        self.worksFiles = WorksFiles()


    def __del__(self):
        self.cap.release()

    def action_detected(self):
        self.controlTime = datetime.now()

        if self.number_whatsapp > 0 and self.controlTime > self.controlTimeAux:
            
            baseDir = self.worksFiles.createDirectoryYMD(settings.STORAGE_TAKE_PICTURE)
            insertPath = os.path.join(settings.STORAGE_TAKE_PICTURE)

            nameFile   = "{}{}".format("DetectPerson_"+str(time.time()),settings.EXTENSION_IMG)
            pathImages = "{}/{}".format(baseDir,nameFile)

            insertPath = pathImages.replace(insertPath,"")
            imagen     = Imagen(imagen_path=insertPath,imagen_name=nameFile,imagen_type=1,imagen_group = 1, imagen_date=timezone.now())
            imagen.save()
            self.savePicture(pathImages)
            urlImagen = settings.DIRECCION_URL_SERVER+"/"+settings.STATIC_URL+"/"+settings.WEB_STORAGE_TAKE_PICTURE+"/"+insertPath
            
            for get_value in self.number_whatsapp:
                print("enviando numero a :",get_value)
                #send_msm_web_whatsapp(get_value,"Persona detectada!",urlImagen)
                #thread_MSN = threading.Thread(target=send_msm_web_whatsapp, args=(get_value,"Persona detectada!",urlImagen))
                #thread_MSN.start()
            self.controlTimeAux = datetime.now() + self.control_seconds
        pass

    def getDetectMove(self):
        if not self.cap.isOpened():
            print("No esta activada la camara")
            exit()

        # Llamada al método
        fgbg = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=False)
        # Deshabilitamos OpenCL, si no hacemos esto no funciona
        cv2.ocl.setUseOpenCL(False)

        while self.cap.isOpened():

            success, frame = self.cap.read()
            if not success:
                break
            estado = "No existe movimiento"
            color = (0,255,0)
            #frame = imutils.resize(frame,width=settings.SIZESHOWCAM)
            fgmask = fgbg.apply(frame)
            # Copiamos el umbral para detectar los contornos
            contornosimg = fgmask.copy()

            # Buscamos contorno en la imagen
            contornos, hierarchy = cv2.findContours(contornosimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            # Recorremos todos los contornos encontrados
            for c in contornos:
                # Eliminamos los contornos más pequeños
                if cv2.contourArea(c) > 10000:
                    estado = "Movimiento detectado!"
                    color = (0,0,255)
                    # Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno
                    (x, y, w, h) = cv2.boundingRect(c)
                    # Dibujamos el rectángulo del bounds
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            #frame_flip = cv2.flip(frame,1)
            cv2.putText(frame, estado , (10, 45),cv2.FONT_HERSHEY_SIMPLEX, 2, color,2)
            ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def detectar_rostro_frontal(self):
        while self.cap.isOpened():
            succes, frame = self.cap.read()
            if succes:
                gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                detectFace  = self.face_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                for (x,y,w,h) in detectFace: #si se detecta un rostro se almacenara en estas variables
                    self.action_detected()

    def detectar_rostro_izq(self):
        while self.cap.isOpened():
            succes, frame = self.cap.read()
            if succes:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faceIzq  = self.side_face_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                for (x,y,w,h) in faceIzq:
                    self.action_detected()
    
    def detectar_rostro_derecho(self):
        while self.cap.isOpened():
            succes, frame = self.cap.read()
            if succes:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sideGray = cv2.flip(gray,1)
                faceDer= self.side_face_detection.detectMultiScale(sideGray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                for (x,y,w,h) in faceDer:
                    self.action_detected()
    
    def detectar_cuerpo(self):
        while self.cap.isOpened():
            succes, frame = self.cap.read()
            if succes:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                detectedBody = self.full_body_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                for (x,y,w,h) in detectedBody:
                    self.action_detected()
                    
    def all_detected(self):
        thread_detectar_rostro_frontal = threading.Thread(target=self.detectar_rostro_frontal)
        thread_detectar_rostro_frontal.start()
        #thread_detectar_rostro_izq = threading.Thread(target=self.detectar_rostro_izq)
        #thread_detectar_rostro_izq.start()
        #thread_detectar_rostro_derecho = threading.Thread(target=self.detectar_rostro_derecho)
        #thread_detectar_rostro_derecho.start()
        #thread_detectar_cuerpo = threading.Thread(target=self.detectar_cuerpo)
        #thread_detectar_cuerpo.start()

    def detectar_persona_Aux(self):

        while self.cap.isOpened():
            succes, frame = self.cap.read()
            if succes:
                self.frame_flip = cv2.flip(frame,1)
                ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, self.frame_flip)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def detectar_persona(self):
        color = (255,0,0)
        thickness = 2
        
        while self.cap.isOpened():
            succes, frame = self.cap.read()

            if succes:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sideGray = cv2.flip(gray,1)
                #detectedBody = self.full_body_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                detectFace   = self.face_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                #detectEyes  = self.eyes_detecttion.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                #sideFace     = self.side_face_detection.detectMultiScale(gray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                #othersideFace= self.side_face_detection.detectMultiScale(sideGray,scaleFactor = settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
                #self.frame_flip = cv2.flip(frame,1)
                self.frame_flip = frame

                #for (x,y,w,h) in detectedBody:
                #    cv2.rectangle(frame,(x,y),(x+w,y+h),color,thickness)
                #    self.action_detected()

                for (x,y,w,h) in detectFace: #si se detecta un rostro se almacenara en estas variables
                    cv2.rectangle(frame,(x,y),(x+w,y+h),color,thickness)
                    self.action_detected()
                    
                #for (x,y,w,h) in sideFace:
                #    cv2.rectangle(frame,(x,y),(x+w,y+h),color,thickness)
                #    self.action_detected()
                    
                #for (x,y,w,h) in othersideFace:
                #    cv2.rectangle(self.frame_flip,(x,y),(x+w,y+h),color,thickness)
                #    self.action_detected()

                #for (x,y,w,h) in detectEyes:
                #   cv2.rectangle(frame,(x,y),(x+w,y+h),color,thickness)

                ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        

    def detectarPersonasddd(self):
        HOGCV = cv2.HOGDescriptor()
        HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        #cv2.startWindowThread()
        
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            bounding_box_cordinates, weights =  HOGCV.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)
            person = 1
            for x,y,w,h in bounding_box_cordinates:
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                cv2.putText(frame, 'person: {}'.format(person), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
                person += 1
                cv2.putText(frame, 'Status : Detecting ', (40,40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)
                cv2.putText(frame, 'Total Persons : {}'.format(person-1), (40,70), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)

            #frame_flip = cv2.flip(frame,1)
            #cv2.putText(frame_flip, estado , (10, 45),cv2.FONT_HERSHEY_SIMPLEX, 2, color,2)
            ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def takePicture(self,count = 0, pathImages = None):
        nameFile = "{}_{}{}".format("TakePicture",count,settings.EXTENSION_IMG)
        pathImages = "{}/{}".format(pathImages,nameFile)
        self.savePicture(pathImages)

    def savePicture(self,pathImages):
        print("pathImages ",pathImages)
        cv2.imwrite(pathImages,self.frame_flip)