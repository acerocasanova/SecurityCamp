import cv2
import os, shutil
import time
import numpy as np
from django.conf import settings

from cam.src.camcontrol.SharedCamera import SharedCamera
from cam.src.camcontrol.streaming import FrameStrategy, mjpeg_stream
from cam.src.camcontrol.strategies import FaceRecognitionStrategy


class FaceCaptureStrategy(FrameStrategy):
    """
    Reemplaza al while enorme que tenia TakeRecordCam.genRecord(): mientras
    se entrena un nuevo registro, va guardando en disco cada rostro
    (frontal, de perfil y de perfil espejado) que detecta -hasta juntar
    `count_max` capturas- y dibuja una barra de progreso sobre el video.
    Es una FrameStrategy con su propio estado (count, progress), tal cual
    lo pensado para este patron: el generador de mjpeg_stream() no sabe
    nada de esta logica, solo le va pasando frames.
    """

    def __init__(self, face_detection, side_face_detection, show_record, count_max=300):
        self.face_detection = face_detection
        self.side_face_detection = side_face_detection
        self.show_record = show_record
        self.count_max = count_max
        self.count = 1
        self.count_aux = 0
        self.progress = 1
        self.color = (255, 0, 0)
        self.thickness = 2
        self.save_path = os.path.join(settings.STORAGE_CAM_RECORD, show_record.image_name)
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def process(self, frame):
        if self.count > self.count_max:
            frame_flip = cv2.flip(frame, 1)
            self._draw_progress(frame_flip, 100, mensaje='proceso Finalizado')
            return frame_flip

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sideGray = cv2.flip(gray, 1)
        auxFrame = frame.copy()

        faces = self.face_detection.detectMultiScale(
            gray, scaleFactor=settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
        sideFace = self.side_face_detection.detectMultiScale(
            gray, scaleFactor=settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
        othersideFace = self.side_face_detection.detectMultiScale(
            sideGray, scaleFactor=settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), self.color, self.thickness)
            self._save_face(auxFrame, x, y, w, h)

        for (x, y, w, h) in sideFace:
            cv2.rectangle(frame, (x, y), (x + w, y + h), self.color, self.thickness)
            self._save_face(auxFrame, x, y, w, h)

        frame_flip = cv2.flip(frame, 1)
        for (x, y, w, h) in othersideFace:
            cv2.rectangle(frame_flip, (x, y), (x + w, y + h), self.color, self.thickness)
            self._save_face(auxFrame, x, y, w, h)

        if self.count % 3 == 0 and self.count != self.count_aux:
            self.progress += 1
            self.count_aux = self.count

        self._draw_progress(frame_flip, self.progress, mensaje='proceso 1 de 1')
        return frame_flip

    def _save_face(self, auxFrame, x, y, w, h):
        rostro = auxFrame[y:y + h, x:x + w]
        try:
            rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            nameFile = "{}/{}_{}{}".format(
                self.save_path, self.show_record.image_name, self.count, settings.EXTENSION_IMG)
            cv2.imwrite(nameFile, rostro)
        except Exception as e:
            print("Warning! Error al capturar una imagen ", str(e))
        self.count += 1

    def _draw_progress(self, frame_flip, percentage, mensaje='procesando', width=700):
        filled_length = int((width * percentage) / 100)
        cv2.rectangle(frame_flip, (0, 0), (filled_length, 50), (0, 255, 0), -1)
        text = "{}% {}".format(percentage, mensaje)
        cv2.putText(frame_flip, text, (10, 38), 1, 3, (255, 0, 0), 3)


class TakeRecordCam(object):

    def __init__(self):
        self.face_detection  = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_frontalface_default.xml'))
        self.side_face_detection = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_profileface.xml'))

        self.cap = SharedCamera.get_camera(0)
        createDirectory = os.path.join(settings.STORAGE_CAM_RECORD)
        if not  os.path.exists(createDirectory):
            os.makedirs(settings.STORAGE_CAM_RECORD)

        createDirectory = os.path.join(settings.DIR_CONFIG_FILES)
        if not  os.path.exists(createDirectory):
            os.makedirs(settings.DIR_CONFIG_FILES)

        self.dirRecordPath = os.listdir(settings.STORAGE_CAM_RECORD)

    def __del__(self):
        self.cap.release()

    def genRecord(self,showRecord):
        """Antes tenia un while enorme con la captura de rostros y la
        barra de progreso escritas inline; ahora es el template
        mjpeg_stream() + FaceCaptureStrategy."""
        strategy = FaceCaptureStrategy(self.face_detection, self.side_face_detection, showRecord)
        return mjpeg_stream(self.cap, [strategy])

    def getVideoEIGENFACE(self):
        """Antes eran ~35 lineas casi identicas a getVideoLBPH/FISHERFACE;
        ahora las tres son FaceRecognitionStrategy con distinto modelo."""
        strategy = FaceRecognitionStrategy('eigen', self.face_detection, self.dirRecordPath)
        return mjpeg_stream(self.cap, [strategy])

    def getVideoLBPH(self):
        strategy = FaceRecognitionStrategy('lbph', self.face_detection, self.dirRecordPath)
        return mjpeg_stream(self.cap, [strategy])

    def getVideoFISHERFACE(self):
        strategy = FaceRecognitionStrategy('fisher', self.face_detection, self.dirRecordPath)
        return mjpeg_stream(self.cap, [strategy])

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
