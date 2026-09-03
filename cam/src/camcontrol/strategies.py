import os
import cv2
import imutils
from django.conf import settings

from cam.src.camcontrol.streaming import FrameStrategy


class FlipStrategy(FrameStrategy):
    """Espeja el frame horizontalmente (cv2.flip con codigo 1)."""

    def process(self, frame):
        return cv2.flip(frame, 1)


class ResizeStrategy(FrameStrategy):
    """Redimensiona manteniendo la relacion de aspecto (a diferencia de
    cv2.resize a un (ancho,alto) fijo, que deforma la imagen)."""

    def __init__(self, width):
        self.width = width

    def process(self, frame):
        return imutils.resize(frame, width=self.width)


class WatermarkStrategy(FrameStrategy):
    """Escribe un texto fijo sobre el frame (ej: el nombre de la camara
    en la grilla de 'Visualizar Camaras')."""

    def __init__(self, text, position=(10, 45), color=(255, 0, 0), scale=2, thickness=2):
        self.text = text
        self.position = position
        self.color = color
        self.scale = scale
        self.thickness = thickness

    def process(self, frame):
        cv2.putText(frame, self.text, self.position, cv2.FONT_HERSHEY_SIMPLEX,
                    self.scale, self.color, self.thickness)
        return frame


class FaceBoxStrategy(FrameStrategy):
    """Detecta rostros con un clasificador Haar y dibuja un recuadro sobre
    cada uno. `on_detect(frame)` es opcional y se invoca una vez por cada
    rostro detectado, para que quien arme el stream decida que hacer
    (ej: DetectMoveCam dispara ahi la alerta de WhatsApp)."""

    def __init__(self, face_cascade, on_detect=None, color=(255, 0, 0), thickness=2):
        self.face_cascade = face_cascade
        self.on_detect = on_detect
        self.color = color
        self.thickness = thickness

    def process(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), self.color, self.thickness)
            if self.on_detect:
                self.on_detect(frame)
        return frame


class MovementDetectionStrategy(FrameStrategy):
    """Sustituye a DetectMoveCam.getDetectMove(): resta de fondo (KNN) +
    deteccion de contornos para marcar zonas en movimiento."""

    def __init__(self, min_area=10000):
        self.min_area = min_area
        self.fgbg = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=False)
        cv2.ocl.setUseOpenCL(False)

    def process(self, frame):
        estado = "No existe movimiento"
        color = (0, 255, 0)

        fgmask = self.fgbg.apply(frame)
        contornos, _ = cv2.findContours(fgmask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in contornos:
            if cv2.contourArea(c) > self.min_area:
                estado = "Movimiento detectado!"
                color = (0, 0, 255)
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.putText(frame, estado, (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)
        return frame


class FaceRecognitionStrategy(FrameStrategy):
    """
    Unifica los tres metodos casi identicos que tenia TakeRecordCam
    (getVideoEIGENFACE / getVideoLBPH / getVideoFISHERFACE): la unica
    diferencia real entre ellos era que algoritmo de reconocimiento facial
    de OpenCV usar y el umbral de confianza para considerar "reconocido".
    Todo lo demas -recortar el rostro, predecir, escribir el nombre o
    'Desconocido'- era identico.
    """

    # nombre -> (constructor del recognizer, setting con el archivo del modelo, umbral)
    MODELOS = {
        'eigen':  (cv2.face.EigenFaceRecognizer_create,  'MODELOEIGENFACE',  5700),
        'lbph':   (cv2.face.LBPHFaceRecognizer_create,   'MODELOLBPHFACE',   90),
        'fisher': (cv2.face.FisherFaceRecognizer_create, 'MODELOFISHERFACE', 500),
    }

    def __init__(self, modelo, face_cascade, dir_record_path):
        crear_recognizer, nombre_setting, umbral = self.MODELOS[modelo]
        self.umbral = umbral
        self.face_cascade = face_cascade
        self.dir_record_path = dir_record_path
        self.recognizer = crear_recognizer()
        self.recognizer.read(os.path.join(settings.DIR_CONFIG_FILES, getattr(settings, nombre_setting)))

    def process(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=settings.SCALE_FACTOR, minNeighbors=settings.MIN_NEIGHBORS)
        frame_flip = cv2.flip(frame, 1)

        for (x, y, w, h) in faces:
            rostro = gray[y:y + h, x:x + w]
            rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            result = self.recognizer.predict(rostro)

            if result[1] < self.umbral:
                try:
                    nombre = self.dir_record_path[result[0]].split("_")
                    cv2.putText(frame_flip, nombre[0], (x, y - 150), 1, 3, (255, 0, 0), 3, cv2.LINE_AA)
                    cv2.putText(frame_flip, nombre[1], (x, y - 100), 1, 3, (255, 0, 0), 3, cv2.LINE_AA)
                    cv2.putText(frame_flip, nombre[2], (x, y - 50), 1, 3, (255, 0, 0), 3, cv2.LINE_AA)
                except Exception:
                    pass
            else:
                cv2.putText(frame_flip, 'Desconocido', (x, y - 20), 2, 0.8, (0, 0, 255), 3, cv2.LINE_AA)

        return frame_flip
