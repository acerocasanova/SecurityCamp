import cv2
from django.conf import settings


class FrameStrategy(object):
    """
    Estrategia de procesamiento de un frame (patron Strategy).

    Cada clase de camcontrol (VideoCam, DetectMoveCam, TakeRecordCam, ...)
    tenia su propio metodo con un "while self.cap.isOpened(): leer frame,
    procesarlo, codificarlo, entregarlo" copiado y pegado, donde solo el
    "procesarlo" cambiaba de un metodo a otro (dibujar un recuadro,
    detectar movimiento, reconocer un rostro, guardar una foto, etc.).

    Una FrameStrategy es justamente ese paso variable, aislado en su
    propia clase. Como es un objeto (no una funcion suelta), puede guardar
    su propio estado entre frames -contadores, modelos ya cargados, el
    substractor de fondo, etc.- sin pisar el de otras estrategias.
    """

    def process(self, frame):
        """
        Recibe el frame BGR leido de la camara y devuelve el frame a
        codificar (puede modificarlo in-place y devolverlo, o devolver
        uno nuevo). Si devuelve None, ese frame se descarta y no se
        codifica ni se envia.
        """
        raise NotImplementedError


def mjpeg_stream(cap, strategies, extension=None):
    """
    Template Method: el esqueleto comun a TODOS los streams MJPEG del
    sitio (antes repetido en cada clase de camcontrol).

    Se encarga de la parte que nunca cambiaba -verificar que la camara
    este abierta, leer frames en bucle, encadenar las `strategies` en
    orden, codificar a JPEG y entregar el frame en el formato multipart
    que esperan los <img src="..."> del sitio- para que cada clase de
    camcontrol solo tenga que declarar QUE estrategias usar.

    `cap` es cualquier objeto con `.isOpened()`/`.read()` (normalmente un
    SharedCamera). `strategies` es una lista de FrameStrategy aplicadas en
    orden: la salida de una es la entrada de la siguiente.
    """
    ext = extension or settings.EXTENSION_IMG

    if not cap.isOpened():
        print("No esta activada la camara")
        return

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        for strategy in strategies:
            frame = strategy.process(frame)
            if frame is None:
                break

        if frame is None:
            continue

        ret, jpeg = cv2.imencode(ext, frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
