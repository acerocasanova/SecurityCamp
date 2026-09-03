"""
Apertura de camaras y streaming MJPEG.

- `SharedCamera`  -> conexion compartida a una camara (una sola por
                     dispositivo/URL, sin importar cuantos navegadores
                     la esten mirando).
- `streaming`     -> mjpeg_stream(), el bucle comun a todos los streams
                     (leer frame -> aplicar estrategias -> codificar).
- `strategies`    -> FrameStrategy concretas y reutilizables (espejar,
                     redimensionar, marca de agua, deteccion de rostro/
                     movimiento, reconocimiento facial).
- `CamareVideoCam`, `CamareVideoIP`, `ShowAllCam`, `DetectMoveCam`,
  `TakeRecordCam`, `TakePictureCam` -> una clase por caso de uso
  (webcam local, camara IP, grilla de camaras, deteccion de movimiento/
  personas, entrenamiento de reconocimiento, captura de fotos/rafaga/
  video), cada una arma su propia lista de estrategias.
- `ShowVideo`     -> reproduccion de un archivo de video ya grabado (no
                     una camara en vivo: no usa SharedCamera a proposito,
                     cada visor necesita su propia posicion de scrub).
- `TypeCam`       -> resuelve la fuente real (indice de dispositivo o
                     URL RTSP) a partir de una camara guardada en la BD.
"""
