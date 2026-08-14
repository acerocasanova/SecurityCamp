from cam.models import Configuration
from django.utils import timezone


class DictonaryConfiguration(object):

    def __init__(self):
        pass

    def list_config_bd(self):
        return Configuration.objects.all()

    def add_config(self,name):
        config = Configuration(c_name = name,c_date = timezone.now())
        config.save()

    def save_update(self,id,value,activate):
        Configuration.objects.filter(pk = id).update(c_value = str(value).strip(), c_activity = activate)

    def find_config(self,name):
        get_value = []
        list = Configuration.objects.filter(c_name = name, c_activity = True)
        for value in list:
            print("Cargando configuraciones ",value.c_value)
            get_value.append(value.c_value)
        return get_value
    
    def find_config(self,name,valor_omision):
        get_value = []
        list = Configuration.objects.filter(c_name = name, c_activity = True)
        if list:
            for value in list:
                print("Cargando configuraciones ",value.c_value)
                get_value.append(value.c_value)
        else:
            return valor_omision
        return get_value

    def find_all_config_activity(self):
        list = Configuration.objects.filter(c_activity = True)
        return list

    def detail_config(self):
        list = [(Web_whatsapp.NUMERO_WEBWHATSAPP,'Agrega un numero para recibir un mensaje, cuando la persona es detectada'),
                (Web_whatsapp.TIEMPO_ENTREME_MSM,'Tiempo que se envia un mensaje por la deteccion de la persona en segundos'),
                (Tomar_foto.DETECTAR_PERSONA,'Guarda una imagen de la persona que a sido detectada'),
                (Tomar_foto.TIEMPO_ENTREME_TOMAR,'Tiempo en que se guarda una foto por persona detectada en segundos'),
                (Servidor.DIRECCION_IP,'Guarda la direccion de ip o dominio para uso informativo'),
                (Servidor.PUERTO,'Guarda la direccion de ip o dominio para uso informativo'),
                (Servidor.PUERTO,'Guarda la direccion de ip o dominio para uso informativo'),
                (Camara.NUMERO_DE_CAMARAS,'Asigna el maximo de camaras que visualizara por pantalla, solo hasta 42'),
                (Camara.TAMANO_CAMARA,'Asigna el tamaño de camaras que vizualizara por pantalla'),
                (Camara.PANTALLA_DINAMICA,'Agrupa tus camaras que deseas visualizar en una pantalla dinamica')]
        return list

class Tomar_foto:
    __slots__ = ()
    DETECTAR_PERSONA = "DETECTAR_PERSONA"
    TIEMPO_ENTREME_TOMAR = "TIEMPO_ENTREME_TOMAR"
    TIEMPO_ENTREME_TOMAR_OMISION = 0

class Web_whatsapp:
    __slots__ = ()
    NUMERO_WEBWHATSAPP = "NUMERO_WEBWHATSAPP"
    TIEMPO_ENTREME_MSM = "TIEMPO_ENTREME_MSM"
    NUMERO_WEBWHATSAPP_OMISION = 0

class Servidor:
    __slots__=()
    DIRECCION_IP = "DIRECCION_IP"
    PUERTO = "PUERTO"

class Camara:
    __slots__=()
    NUMERO_DE_CAMARAS = "NUMERO_DE_CAMARAS"
    NUMERO_DE_CAMARAS_OMISION = 1
    TAMANO_CAMARA = "TAMANO_CAMARA"
    TAMANO_POR_CAMARA_OMISION = 320
    PANTALLA_DINAMICA = "PANTALLA_DINAMICA"
    
