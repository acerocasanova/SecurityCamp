
from django.core.exceptions import ValidationError
from cam.models import Record, AgregarCamara
from django import forms
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib.admin.widgets import AdminDateWidget
from django.conf import settings
import datetime

class BotonForm(forms.Form):
    btn = forms.CharField()

class UpdateRecord(forms.ModelForm):
    CHOISE_LEVEL_DANG = (
        ('0', 'Normal'),
        ('1', 'Leve'),
        ('2', 'Peligroso'),
    )
    #first_name = forms.CharField(max_length=100,label = 'Nombres')
    #last_name = forms.CharField(max_length=100,label = 'Aperllidos')
    date_of_birth = forms.DateField(
                    initial=datetime.date.today,
                    label='Fecha de Nacimiento',
                    localize=True,
                    required=False,
                    widget=forms.DateInput(format='%Y-%m-%d')
                )
    #rut = forms.IntegerField(label='Rut persona')
    #dv  = forms.CharField(max_length=1,label='DV')
    apartament = forms.IntegerField(label='Numero Apartamento')
    level_dangerous = forms.ChoiceField(label='Niverl de Peligro',choices=CHOISE_LEVEL_DANG)
    phone_number = forms.IntegerField(label='Numero de Telefono')
    
    class Meta:
        model = Record
        fields = ['date_of_birth','apartament','level_dangerous','phone_number']


class CreateRecord(forms.ModelForm):
    #YEARS= [x for x in range(1940,2023)]
    CHOISE_LEVEL_DANG = (
        ('0', 'Normal'),
        ('1', 'Leve'),
        ('2', 'Peligroso'),
    )
    first_name = forms.CharField(max_length=100,label = 'Nombres')
    last_name = forms.CharField(max_length=100,label = 'Aperllidos')
    date_of_birth = forms.DateField(
                    initial=datetime.date.today,
                    label='Fecha de Nacimiento',
                    localize=True,
                    required=False,
                    widget=forms.DateInput(format='%Y-%m-%d')
                )
    rut = forms.IntegerField(label='Rut persona')
    dv  = forms.CharField(max_length=1,label='DV')
    apartament = forms.IntegerField(label='Numero Apartamento')
    level_dangerous = forms.ChoiceField(label='Niverl de Peligro',choices=CHOISE_LEVEL_DANG)
    phone_number = forms.IntegerField(label='Numero de Telefono')
    #image_name = forms.CharField(max_length=230)
    
    class Meta:
        model  = Record
        fields = ['first_name','last_name','date_of_birth','rut','dv','apartament','level_dangerous','phone_number']
        #order_fields = ['first_name','last_name','date_of_birth','rut','dv','apartament','level_dangerous','phone_number']
        #exclude = ['image_name']
        #fields = "__all__"


class CreateCam(forms.ModelForm):

    a_tipo_cam = forms.IntegerField()
    a_ip   = forms.CharField(max_length=30)
    a_port = forms.IntegerField()
    a_name_port = forms.CharField(max_length=30)
    a_user = forms.CharField(max_length=40)
    a_pass = forms.CharField(max_length=100)
    a_channel = forms.IntegerField()
    a_tipo_transmision = forms.IntegerField()
    a_activity = forms.BooleanField()
    a_name = forms.CharField(max_length=100)

    class Meta:
        model = AgregarCamara
        fields = ['a_tipo_cam','a_ip','a_port','a_name_port','a_user','a_pass','a_channel','a_tipo_transmision','a_activity','a_name' ]