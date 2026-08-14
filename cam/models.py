from django.db import models
from django.urls import reverse  # To generate URLS by reversing URL patterns

class Record(models.Model):
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    rut = models.IntegerField(blank=False,null=False,default=6666666)
    apartament = models.IntegerField(blank=True,default=0)
    level_dangerous = models.IntegerField(default=0)
    phone_number = models.IntegerField(default=0)
    path = models.CharField(max_length=200)
    date_register = models.DateField(null=True, blank=True)
    image_name = models.CharField(max_length=230)

    def get_absolute_url(self):
        return reverse('showRecord', args=[self.id])
    
    def get_takePicture(self):
        return reverse('takePictureRecord', args=[self.id])
    
    def get_takeRecord(self):
        return reverse('takeRecord', args=[self.id])
    
    def get_delete_url(self):
        return reverse('deleteRecord', args=[str(self.id)])
    
    def get_update_url(self):
        return reverse('updateRecord',args=[str(self.id)])
    
    def get_showVideoCamTakeRecord(self):
        return reverse('showVideoCamTakeRecord', args=[self.id])


class Imagen(models.Model):
    
    #imagen_insert_date  = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    imagen_name  = models.CharField(max_length=100)
    imagen_path  = models.CharField(max_length=100)
    imagen_date  = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    #imagen_date  = models.DateField(null=True, blank=True)
    imagen_type  = models.IntegerField(blank=False,null=False,default=0)
    imagen_group = models.IntegerField(blank=False,null=False,default=0)
    imagen_id    = models.IntegerField(blank=False,null=False,default=0)

    def get_absolute_url(self):
        return reverse('showImage', args=[self.id])

    def get_delete_url(self):
        return reverse('deleteImagen', args=[str(self.id)])

class Configuration(models.Model):

    c_group_id = models.IntegerField(blank=False,null=False,default=0)
    c_type_n   = models.IntegerField(blank=False,null=False,default=0)
    c_type_c   = models.CharField(max_length=10)
    c_name     = models.CharField(max_length=100)
    c_value    = models.CharField(max_length=200)
    c_activity = models.BooleanField(default=False)
    c_agregado = models.BooleanField(default=True)
    c_date     = models.DateTimeField(blank=True,null=True,auto_now_add=True)

    def get_delete_url(self):
        return reverse('configDelete', args=[str(self.id)])

class AgregarCamara(models.Model):

    a_id = models.IntegerField(blank=False,null=False,default=0)
    a_tipo_cam = models.IntegerField(blank=False,null=False,default=0)
    a_ip   = models.CharField(max_length=30)
    a_port = models.IntegerField(blank=False,null=False,default=0)
    a_name_port = models.CharField(max_length=30)
    a_user = models.CharField(max_length=40)
    a_pass = models.CharField(max_length=100)
    a_channel = models.IntegerField(blank=False,null=False,default=0)
    a_tipo_transmision = models.IntegerField(blank=False,null=False,default=0)
    a_activity = models.BooleanField(default=False)
    a_name = models.CharField(max_length=100)
    a_date = models.DateTimeField(blank=True,null=True,auto_now_add=True)

    def get_delete_url(self):
        return reverse('configDeleteCam', args=[str(self.id)])
