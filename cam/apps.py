from django.apps import AppConfig
from django.conf import settings

class CamConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cam"
    #print("iniciando servidor Cam")

def getConfiguraciones(request):
    return {'tamanoVideo': 800, 'MEDIA_URL': settings.MEDIA_URL}
