import threading
import cv2


class SharedCamera(object):
    """
    Envoltorio compartido sobre cv2.VideoCapture.

    Problema que resuelve: cada vista (VideoCam, VideoIP, DetectMoveCam,
    ShowAllCam, TakeRecordCam, TakePictureCamp, ...) abria su propio
    cv2.VideoCapture(source) en cada request. La mayoria de las camaras
    (webcam local o IP) solo aceptan UNA conexion activa a la vez, asi que
    al abrir el sitio en un segundo navegador/pestaña, el segundo
    VideoCapture fallaba (y a veces tambien rompia al primero).

    Con SharedCamera, todos los visores de una misma fuente (mismo indice
    de dispositivo o misma URL RTSP) comparten una unica conexion real. Un
    hilo en segundo plano lee frames en forma continua y cada visor
    simplemente toma una copia del ultimo frame disponible, sin volver a
    tocar el dispositivo.

    Uso: reemplaza `self.cap = cv2.VideoCapture(source)` por
    `self.cap = SharedCamera.get_camera(source)`. El resto del codigo que
    ya usa `self.cap.isOpened()/.read()/.set()/.get()/.release()` sigue
    funcionando igual, sin mas cambios.
    """

    _instances = {}
    _registry_lock = threading.Lock()

    def __init__(self, source):
        self.source = source
        self.cap = cv2.VideoCapture(source)
        self._frame = None
        self._frame_lock = threading.Lock()
        self._viewers = 0
        self._running = True
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    @classmethod
    def get_camera(cls, source):
        """Devuelve la conexion compartida para `source`, creandola si hace falta."""
        key = str(source)
        with cls._registry_lock:
            instance = cls._instances.get(key)
            if instance is None or not instance.cap.isOpened():
                instance = cls(source)
                cls._instances[key] = instance
            instance._viewers += 1
            return instance

    def _update_loop(self):
        while self._running and self.cap.isOpened():
            success, frame = self.cap.read()
            if success:
                with self._frame_lock:
                    self._frame = frame

    def isOpened(self):
        return self.cap.isOpened()

    def read(self):
        with self._frame_lock:
            if self._frame is None:
                return False, None
            return True, self._frame.copy()

    def set(self, prop, value):
        return self.cap.set(prop, value)

    def get(self, prop):
        return self.cap.get(prop)

    def release(self):
        """
        Un visor termino de mirar. No cerramos el dispositivo real: puede
        haber otros navegadores/pestañas usando esta misma camara. La
        conexion queda abierta mientras el servidor este corriendo.
        """
        with self._registry_lock:
            self._viewers = max(0, self._viewers - 1)
