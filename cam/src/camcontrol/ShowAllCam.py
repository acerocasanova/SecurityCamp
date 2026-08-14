import cv2
from django.conf import settings

from cam.src.configuracion.AgregarCamara import ConfiguracionAgregarCamara
from cam.src.camcontrol.TypeCam import GetTypeCam

class ShowAllCam(object):

    def __init__(self, idCam):
        cam = ConfiguracionAgregarCamara()
        self.showCam = cam.get_find_cam(idCam)
        getTypeCam = GetTypeCam()
        if self.showCam.a_tipo_cam == 0:
            self.cap = cv2.VideoCapture(getTypeCam.get_cam_integrada(self.showCam))
        elif idCam != 0 and self.showCam.a_tipo_cam == 1:
            self.cap = cv2.VideoCapture(getTypeCam.get_cam_ip(self.showCam))

    def __del__(self):
        self.cap.release()

    def get_video(self):
        color = (255,0,0)
        while self.cap.isOpened():
            succes, frame = self.cap.read()
            if succes:
                cv2.putText(frame, self.showCam.a_name , (10, 45),cv2.FONT_HERSHEY_SIMPLEX, 2, color,2)
                ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, frame)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')