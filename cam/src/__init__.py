"""
Codigo de negocio de la app `cam`, separado de las capas estandar de
Django (views.py, models.py, urls.py, ...).

Subpaquetes:
- `camcontrol`   -> apertura de camaras, streaming MJPEG, deteccion y
                    reconocimiento facial.
- `configuracion`-> lectura/escritura de configuracion del sitio y de
                    camaras guardadas en la base de datos.
- `forms`        -> formularios de Django.
- `utils`        -> utilidades generales (fechas, archivos, barra de
                    progreso, etc.).
"""
