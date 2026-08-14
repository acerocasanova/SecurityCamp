from django.contrib import admin
from .models import Record, Imagen, Configuration, AgregarCamara

admin.site.register(AgregarCamara)
admin.site.register(Record)
admin.site.register(Imagen)
admin.site.register(Configuration)



# Register your models here.
