from cam.models import AgregarCamara
from django.utils import timezone
import json


class ConfiguracionAgregarCamara(object):
    
    def __init__(self):
        pass
    
    def list_config_bd(self):
        return AgregarCamara.objects.all()

    def add_config(self,tipo_cam):
        config = AgregarCamara(a_tipo_cam = tipo_cam,a_date = timezone.now())
        config.save()

    def save_update_cam_integrada(self,addCam):
        AgregarCamara.objects.filter(pk = addCam.id).update(a_name = str(addCam.a_name).strip(), a_channel = addCam.a_channel, a_activity = addCam.a_activity)

    def save_update_cam_ip(self,addCam):
        AgregarCamara.objects.filter(pk = addCam.id).update(a_name = str(addCam.a_name).strip(),a_ip = str(addCam.a_ip).strip(), a_user = str(addCam.a_user).strip(),a_pass = str(addCam.a_pass).strip(),
                                                     a_channel = addCam.a_channel,a_tipo_transmision= addCam.a_tipo_transmision,a_port=addCam.a_port, a_activity = addCam.a_activity)

    def find_config_show(self):
        list = AgregarCamara.objects.values("id","a_name","a_tipo_cam")
        return list
    
    def get_list_id_activate(self):
        list = AgregarCamara.objects.filter(a_activity = True).values("id")
        return list
    
    def get_find_cam(self, id):
         return AgregarCamara.objects.filter(pk = id, a_activity = True)[0]

    def find_all_config_activity(self):
        list = AgregarCamara.objects.filter(a_activity = True)
        return list

    def detail_config(self):
        list = [(Add_cam.AGREGAR_CAMARA_IP,'Agrega una camara ip con credenciales usuario y contraseña para controlar y detectar'),
                (Add_cam.AGREGAR_CAMARA_COMPUTADOR,'Agrega tu camara de tu computador para controlar y detectar')]
        return list

    def get_totPantalla(self,cam_activate, tot_cam_por_pantalla):
        list = [cam_activate[i : i + tot_cam_por_pantalla] for i in range(0, len(cam_activate), tot_cam_por_pantalla)]
        return list

class Add_cam:
    __slots__=()
    AGREGAR_CAMARA_IP = "AGREGAR_CAMARA_IP"
    AGREGAR_CAMARA_COMPUTADOR = "AGREGAR_CAMARA_COMPUTADOR"