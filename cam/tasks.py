from celery import shared_task
from time import sleep
from celery_progress.backend import ProgressRecorder
from django.conf import settings
import os, cv2
from datetime import datetime
import requests
import numpy as np


@shared_task(bind=True)
def go_to_sleep(self,duration):
    print("duracion ",duration)
    progress_recorder = ProgressRecorder(self)
    for i in range(5):
        sleep(duration)
        progress_recorder.set_progress(i + 1, 5, f'On iteration {i}')
    return 'Done'

@shared_task(bind=True)
def send_msm_web_whatsapp(self,number,message,file):

    if(number != None and message != None):
        
        headers = {'Content-Type':'application/json'}
        data = {
            "message": message,
            "phone": number,
            "urlFile" : str(file)
        }
        print(data)
        response = requests.post(settings.DIRECCION_URL_WEB_WATSAAP, json=data, headers=headers)
        print(response)

    return 'Done'


@shared_task(bind=True)
def trainRecordBarLBPH(self):
    progress_recorder = ProgressRecorder(self)
    labels = []
    faceData = []
    label = 0
    endCount = 4
    dirRecordPath = os.listdir(settings.STORAGE_CAM_RECORD)
    progress_recorder.set_progress(1, endCount, 'Procesando lectura LBPH')
    for nameDir  in dirRecordPath:
        personPath = str(settings.STORAGE_CAM_RECORD) + '/' + nameDir
        for fileName in os.listdir(personPath):
            labels.append(label)
            faceData.append(cv2.imread(personPath+'/'+fileName,0))
        label = label + 1
    progress_recorder.set_progress(2, endCount, 'Procesando reconocimiento LBPH')
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    progress_recorder.set_progress(3, endCount, 'Calculando y Procesando reconocimiento LBPH')
    face_recognizer.train(faceData,np.array(labels))
    progress_recorder.set_progress(4, endCount, 'Integrando reconocimiento LBPH')
    face_recognizer.write(os.path.join(settings.DIR_CONFIG_FILES, settings.MODELOLBPHFACE))
    return "Completado!"


@shared_task(bind=True)
def trainRecordBarEIGENFACE(self,seconds):
    progress_recorder = ProgressRecorder(self)
    labels = []
    faceData = []
    label = 0
    endCount = 4
    dirRecordPath = os.listdir(settings.STORAGE_CAM_RECORD)
    progress_recorder.set_progress(1, endCount, 'Procesando lectura EIGENFACE')
    for nameDir  in dirRecordPath:
        personPath = str(settings.STORAGE_CAM_RECORD) + '/' + nameDir
        for fileName in os.listdir(personPath):
            labels.append(label)
            faceData.append(cv2.imread(personPath+'/'+fileName,0))
        label = label + 1
    progress_recorder.set_progress(2, endCount, 'Procesando reconocimiento EIGENFACE')
    face_recognizer = cv2.face.EigenFaceRecognizer_create()
    progress_recorder.set_progress(3, endCount, 'Calculando y Procesando reconocimiento EIGENFACE')
    face_recognizer.train(faceData,np.array(labels))
    progress_recorder.set_progress(4, endCount, 'Integrando reconocimiento EIGENFACE')
    face_recognizer.write(os.path.join(settings.DIR_CONFIG_FILES, settings.MODELOEIGENFACE))
    return "Completado!"



@shared_task(bind=True)
def trainRecordBarFisherFace(self,seconds):
    progress_recorder = ProgressRecorder(self)
    labels = []
    faceData = []
    label = 0
    endCount = 4
    dirRecordPath = os.listdir(settings.STORAGE_CAM_RECORD)
    progress_recorder.set_progress(1, endCount, 'Procesando lectura FisherFace')
    for nameDir  in dirRecordPath:
        personPath = str(settings.STORAGE_CAM_RECORD) + '/' + nameDir
        for fileName in os.listdir(personPath):
            labels.append(label)
            faceData.append(cv2.imread(personPath+'/'+fileName,0))
        label = label + 1
    progress_recorder.set_progress(2, endCount, 'Procesando reconocimiento FisherFace')
    face_recognizer = cv2.face.FisherFaceRecognizer_create()
    progress_recorder.set_progress(3, endCount, 'Calculando y Procesando reconocimiento FisherFace')
    #con este metodo tengo que tener a lo menos dos personas registradas o me da un error (Reason: Only one class was given! in function 'lda')
    face_recognizer.train(faceData,np.array(labels))
    progress_recorder.set_progress(4, endCount, 'Integrando reconocimiento FisherFace')
    face_recognizer.write(os.path.join(settings.DIR_CONFIG_FILES, settings.MODELOFISHERFACE))
    return "Completado!"