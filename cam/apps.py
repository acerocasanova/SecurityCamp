from django.apps import AppConfig

class CamConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cam"
    #print("iniciando servidor Cam")

def getConfiguraciones(request):
    return {'tamanoVideo': 800} 
