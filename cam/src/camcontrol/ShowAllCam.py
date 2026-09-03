import cv2
from django.conf import settings

from cam.src.configuracion.AgregarCamara import ConfiguracionAgregarCamara
from cam.src.camcontrol.TypeCam import GetTypeCam
from cam.src.camcontrol.SharedCamera import SharedCamera
from cam.src.camcontrol.streaming import mjpeg_stream
from cam.src.camcontrol.strategies import WatermarkStrategy

class ShowAllCam(object):

    def __init__(self, idCam):
        cam = ConfiguracionAgregarCamara()
        self.showCam = cam.get_find_cam(idCam)
        getTypeCam = GetTypeCam()
        if self.showCam.a_tipo_cam == 0:
            self.cap = SharedCamera.get_camera(getTypeCam.get_cam_integrada(self.showCam))
        elif idCam != 0 and self.showCam.a_tipo_cam == 1:
            self.cap = SharedCamera.get_camera(getTypeCam.get_cam_ip(self.showCam))

    def __del__(self):
        self.cap.release()

    def get_video(self):
        """Camara individual dentro de la grilla de 'Visualizar Camaras'.
        Antes tenia su propio while+encode+yield; ahora es el template
        mjpeg_stream() + la estrategia que escribe el nombre de la camara."""
        return mjpeg_stream(self.cap, [WatermarkStrategy(self.showCam.a_name)])
