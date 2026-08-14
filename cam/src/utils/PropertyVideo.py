import cv2
from cam.src.utils.ConversionFechas import  segundos_a_segundos_minutos_y_horas

class PropertyVideo(object):

    def __init__(self):
        self.cap = None
        self.duracionTotSegundos = 0
        self.duracionEnTiempo = 0
        self.widthVideo = 0
        self.heightVideo = 0
        self.totalFrames = 0
        self.totalFPS = 0
        
    def __del__(self):
        pass
    
    def getDuracionToSegundos(self):
        return int(self.duracionTotSegundos)
    def getDuracionEnTiempo(self):
        return self.duracionEnTiempo
    def getWidthVideo(self):
        return int(self.widthVideo)
    def getHeightVideo(self):
        return int(self.heightVideo)
    def getTotalFrames(self):
        return int(self.totalFrames)
    def getTotalFPS(self):
        return int(self.totalFPS)

    def readVideo(self,path):
        self.cap = cv2.VideoCapture(str(path))
        self.duracionTotSegundos = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.cap.get(cv2.CAP_PROP_FPS))
        self.widthVideo  = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.heightVideo = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.totalFrames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.totalFPS    = self.cap.get(cv2.CAP_PROP_FPS)
        self.duracionEnTiempo = segundos_a_segundos_minutos_y_horas(self.duracionTotSegundos)