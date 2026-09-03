import os,cv2
from django.conf import settings
from cam.src.utils.WorksFiles import WorksFiles
from cam.src.camcontrol.SharedCamera import SharedCamera
from cam.src.camcontrol.streaming import FrameStrategy, mjpeg_stream


class TakePictureStrategy(FrameStrategy):
    """
    Reemplaza el if/elif por 'proceso' que tenia TakePictureCamp.getVideo:
    cada objeto de esta estrategia representa UN pedido de la interfaz
    (solo mirar, tomar una foto, una rafaga, o grabar un video) y sabe que
    hacer con cada frame que le llega.

    proceso: 0 = solo mirar, 1 = una foto, 2 = rafaga, 3 = grabar video,
    cualquier otro valor = ya termino (muestra "Proceso completado").
    """

    def __init__(self, proceso, cap, pathImages=None, cant_picture=100):
        self.proceso = proceso
        self.cap = cap
        self.pathImages = pathImages
        self.cant_picture = cant_picture
        self.count = 0
        self.frame_flip = None
        self.writeVideo = None

        if proceso == 3:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
            self.writeVideo = cv2.VideoWriter(
                pathImages, cv2.VideoWriter_fourcc(*'XVID'), 20.0,
                (int(self.cap.get(3)), int(self.cap.get(4))))

    def process(self, frame):
        self.frame_flip = cv2.flip(frame, 1)

        if self.proceso == 0:
            pass
        elif self.proceso == 1:
            self.savePicture(self.pathImages)
            self.proceso = -1
        elif self.proceso == 2 and self.count < self.cant_picture:
            try:
                self.takePicture(self.count, self.pathImages)
                self.createProgressBar(self.count)
            except Exception as e:
                print("Warning! Error al capturar una imagen ", str(e))
            self.count += 1
        elif self.proceso == 3:
            self.writeVideo.write(self.frame_flip)
        else:
            self.createProgressBar(100, "Proceso completado")

        return self.frame_flip

    def createProgressBar(self, percentage, mensaje='procesando', width=700):
        color = (0, 255, 0)
        filled_length = 0
        if percentage > -1:
            filled_length = int((width * percentage) / 100)
            mensaje = "{}% {}".format(percentage, mensaje)
        cv2.rectangle(self.frame_flip, (0, 0), (filled_length, 50), color, -1)
        cv2.putText(self.frame_flip, mensaje, (10, 38), 1, 3, (255, 0, 0), 3)

    def takePicture(self, count=0, pathImages=None):
        nameFile = "{}_{}{}".format("TakePicture", count, settings.EXTENSION_IMG)
        pathImages = "{}/{}".format(pathImages, nameFile)
        self.savePicture(pathImages)

    def savePicture(self, pathImages):
        print("pathImages ", pathImages)
        cv2.imwrite(pathImages, self.frame_flip)

    def release(self):
        """Cierra el archivo de video si esta estrategia estaba grabando
        uno (proceso == 3). Lo llama TakePictureCamp.__del__."""
        if self.writeVideo is not None:
            self.writeVideo.release()


class TakePictureCamp(object):

    def __init__(self):
        self.cap = SharedCamera.get_camera(0)
        self.strategy = None

        savePath = os.path.join(settings.STORAGE_TAKE_PICTURE)
        if not  os.path.exists(savePath):
            os.makedirs(settings.STORAGE_TAKE_PICTURE)

    def __del__(self):
        if self.strategy is not None:
            self.strategy.release()
        self.cap.release()
        cv2.destroyAllWindows()

    def getVideo(self,proceso = 0,cantPicture = 100, pathImages = None):
        """Antes tenia su propio while con un if/elif gigante segun el
        'proceso' pedido; ahora es el template mjpeg_stream() +
        TakePictureStrategy."""
        self.strategy = TakePictureStrategy(proceso, self.cap, pathImages, cantPicture)
        return mjpeg_stream(self.cap, [self.strategy])
