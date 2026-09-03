from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import StreamingHttpResponse
from cam.src.camcontrol.CamareVideoCam import VideoCam
from cam.src.camcontrol.TakeRecordCam import TakeRecordCam
from cam.src.camcontrol.DetectMoveCam import DetectMoveCam
from cam.src.camcontrol.CamareVideoIP import VideoIP
from cam.src.camcontrol.TakePictureCam import TakePictureCamp
from cam.src.camcontrol.ShowVideo import ShowVideo
from cam.src.camcontrol.ShowAllCam import ShowAllCam

from cam.src.utils.WorksFiles import WorksFiles
from cam.src.configuracion.Configuracion import DictonaryConfiguration,Camara
from cam.src.configuracion.AgregarCamara import ConfiguracionAgregarCamara,Add_cam


from .models import Record, Imagen, Configuration, AgregarCamara
from .src.forms.recordForm import CreateRecord, BotonForm, UpdateRecord, CreateCam
from django.shortcuts import redirect
from django.utils import timezone
from django.http import Http404,HttpResponse
import os, time
from datetime import datetime
from django.conf import settings
from .tasks import trainRecordBarLBPH,trainRecordBarFisherFace
from cam.src.utils.PropertyVideo import PropertyVideo
import shutil


videoCam = None
varShowVideo = None

def index(request):
    return render(request, 'index.html')

def showVideoCam(request):
    global videoCam
    videoCam = VideoCam()
    return StreamingHttpResponse(videoCam.stream(),content_type='multipart/x-mixed-replace; boundary=frame')

def showAllCam(request,idCam):
    showAll = ShowAllCam(idCam)
    return StreamingHttpResponse(showAll.get_video(),content_type='multipart/x-mixed-replace; boundary=frame')

def showDetectedRecord(request):
    personDetected = TakeRecordCam()
    return StreamingHttpResponse(personDetected.getVideoFISHERFACE(),content_type='multipart/x-mixed-replace; boundary=frame')

def showVideoCamTakeRecord(request,pk):
    showRecord = Record.objects.get(id=pk)
    videoCamTakeRecord = TakeRecordCam()
    return StreamingHttpResponse(videoCamTakeRecord.genRecord(showRecord),content_type='multipart/x-mixed-replace; boundary=frame')

def showDetectedMove(request,idCam):
    detectMoveCam = DetectMoveCam(idCam)
    return StreamingHttpResponse(detectMoveCam.getDetectMove(),content_type='multipart/x-mixed-replace; boundary=frame')

def showDetectedPerson(request,idCam):
    detectMoveCam = DetectMoveCam(idCam)
    return StreamingHttpResponse(detectMoveCam.detectar_persona(),content_type='multipart/x-mixed-replace; boundary=frame')

def showVideo(request,id,option,numeroFrames,velocidad):
    global varShowVideo
    varShowVideo = ShowVideo()
    image = get_object_or_404(Imagen, pk=id)
    path  = str(settings.STORAGE_TAKE_PICTURE)+"/"+image.imagen_path
    return StreamingHttpResponse(varShowVideo.getVideo(path,option,numeroFrames,velocidad),content_type='multipart/x-mixed-replace; boundary=frame')

def showTakePicture(request,proceso):
    global takePictureCamp
    worksFiles = WorksFiles()
    baseDir = worksFiles.createDirectoryYMD(settings.STORAGE_TAKE_PICTURE)
    takePictureCamp = TakePictureCamp()
    pathImages = None
    insertPath = os.path.join(settings.STORAGE_TAKE_PICTURE)

    if proceso == 1 :
        nameFile   = "{}{}".format("TakePicture_"+str(time.time()),settings.EXTENSION_IMG)
        pathImages = "{}/{}".format(baseDir,nameFile)
        insertPath = worksFiles.convPath(pathImages,insertPath)
        imagen = Imagen(imagen_path=insertPath,imagen_name=nameFile,imagen_type=1,imagen_date=timezone.now())
        imagen.save()

    elif proceso == 2:
        pathImages = worksFiles.createDirectoryNanoSegundos(baseDir)
        insertPath = worksFiles.convPath(pathImages,insertPath)
        imagen = Imagen(imagen_path=insertPath,imagen_name='Directory',imagen_type=2,imagen_date=timezone.now())
        imagen.save()

    elif proceso == 3:
        nameFile   = "{}{}".format("VideoRecord_"+str(time.time()),settings.EXTENSION_AVI)
        pathImages = "{}/{}".format(baseDir,nameFile)
        insertPath = worksFiles.convPath(pathImages,insertPath)
        imagen = Imagen(imagen_path=insertPath,imagen_name=nameFile,imagen_type=3,imagen_date=timezone.now())
        imagen.save()

    return StreamingHttpResponse(takePictureCamp.getVideo(proceso= proceso,pathImages = pathImages),content_type='multipart/x-mixed-replace; boundary=frame')

def showVideoIP(request):
    return StreamingHttpResponse(VideoIP().stream(),content_type='multipart/x-mixed-replace; boundary=frame')

def show_pantalla(request, numero):
    config = DictonaryConfiguration()
    numero_camaras = config.find_config(Camara.NUMERO_DE_CAMARAS,Camara.NUMERO_DE_CAMARAS_OMISION)
    tamano_camaras = config.find_config(Camara.TAMANO_CAMARA,Camara.TAMANO_POR_CAMARA_OMISION)
    configCam = ConfiguracionAgregarCamara()
    list_id = configCam.get_list_id_activate()
    list_total_pantallas = configCam.get_totPantalla(list_id,numero_camaras)
    print(list_total_pantallas)
    return render(request,'showCam/pantalla.html',{'tamano_camaras':tamano_camaras,'total_pantallas':list_total_pantallas[numero]})

def showCamIndex(request):
    config = DictonaryConfiguration()
    numero_camaras = config.find_config(Camara.NUMERO_DE_CAMARAS,Camara.NUMERO_DE_CAMARAS_OMISION)
    tamano_camaras = config.find_config(Camara.TAMANO_CAMARA,Camara.TAMANO_POR_CAMARA_OMISION)
    configCam = ConfiguracionAgregarCamara()
    list_id = configCam.get_list_id_activate()
    list_total_pantallas = configCam.get_totPantalla(list_id,numero_camaras)
    print("total de pantallas "+str(list_total_pantallas))

    return render(request,'showCam/index.html',{'list_id':list_id,
                                                'total_pantallas':list_total_pantallas,
                                                'numero_camaras':numero_camaras,
                                                'tamano_camaras':tamano_camaras})


def configCam(request):
    config = ConfiguracionAgregarCamara()
    show_list_config_bd = None
    show_list_Config = None
    check = True
    if request.method == 'POST':
        form = BotonForm(request.POST)
        if form.is_valid and request.POST.get('btn') == 'agregar':
            valor = request.POST.get('list_config')
            if valor == Add_cam.AGREGAR_CAMARA_COMPUTADOR:
                config.add_config(0)
            elif valor == Add_cam.AGREGAR_CAMARA_IP:
                config.add_config(1)
        elif form.is_valid and request.POST.get('btn') == 'GuardarCamIntegrada':
            addCam = AgregarCamara()
            addCam.id = request.POST.get('id')
            addCam.a_name = request.POST.get('nombre')
            addCam.a_channel = request.POST.get('numero')
            addCam.a_activity = True
            if request.POST.get("activo") == None:
                addCam.a_activity = False
            config.save_update_cam_integrada(addCam)
        elif form.is_valid and request.POST.get('btn') == 'GuardarCamIp':
            addCam = AgregarCamara()
            addCam.id = request.POST.get('id')
            addCam.a_name = request.POST.get('nombre')
            addCam.a_ip = request.POST.get('ip')
            addCam.a_user = request.POST.get('usuario')
            addCam.a_pass = request.POST.get('clave')
            addCam.a_channel = request.POST.get('canal')
            addCam.a_tipo_transmision = request.POST.get('transmision')
            addCam.a_port = request.POST.get('puerto')
            addCam.a_activity = True
            if request.POST.get("activo") == None:
                addCam.a_activity = False
            config.save_update_cam_ip(addCam)

    show_list_Config    = config.detail_config()
    show_list_config_bd = config.list_config_bd()

    return render(request,'config/addCam.html',{'show_list_config_bd':show_list_config_bd,'show_list_Config':show_list_Config})

def configDeleteCam(request, id):
    cam = AgregarCamara.objects.get(id=id)
    if request.method == 'POST':
        cam.delete()
        return redirect('configCam')
    return render(request,'config/deleteCam.html', {'cam': cam})


def configDelete(request, id):
    config = Configuration.objects.get(id=id)
    if request.method == 'POST':
        config.delete()
        return redirect('configIndex')
    return render(request,'config/delete.html', {'config': config})

def configIndex(request):
    config = DictonaryConfiguration()
    show_list_config_bd = None
    show_list_Config = None
    check = True
    value = None

    if request.method == 'POST':
        form = BotonForm(request.POST)
        if form.is_valid and request.POST.get('btn') == 'agregar':
            valor = request.POST.get('list_config')
            config.add_config(valor)
        elif form.is_valid and request.POST.get('btn') == 'guardar':
            show_list_config_bd = config.list_config_bd()
            for list in show_list_config_bd:
                check = True
                value = request.POST.get("valor"+str(list.id))
                print("valor ",value)
                if value:
                    if request.POST.get("check"+str(list.id)) == None:
                        check = False
                    config.save_update(list.id,value,check)

    show_list_Config    = config.detail_config()
    show_list_config_bd = config.list_config_bd()

    return render(request,'config/index.html',{'show_list_config_bd':show_list_config_bd,'show_list_Config':show_list_Config})

def downloadFile(request, id):
    image = get_object_or_404(Imagen, pk=id)
    file_path = str(settings.STORAGE_TAKE_PICTURE)+"/"+image.imagen_path
    if os.path.isdir(file_path):
        outFile = str(settings.STORAGE_TMP)+"/dir_"+str(time.time())+"_"+str(id)
        shutil.make_archive(outFile, 'zip', file_path)
        file_path = outFile+".zip"

    print(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def showControlVideo(request,id):
    global varShowVideo
    listProceso = [0,1,2,3,4,5,6]
    option = 0
    numeroFrames = 0
    velocidad = 0

    image = get_object_or_404(Imagen, pk=id)
    path  = str(settings.STORAGE_TAKE_PICTURE)+"/"+image.imagen_path
    propertyVideo = PropertyVideo()
    propertyVideo.readVideo(path)
    
    if varShowVideo != None:
        numeroFrames = int(varShowVideo.getNumeroFrames())
        velocidad = int(varShowVideo.getVelocidad())

    if request.method == 'POST':
        form = BotonForm(request.POST)
        if form.is_valid and request.POST.get('btn') == 'reset':
            option = listProceso[1]
        elif form.is_valid and request.POST.get('btn') == 'play':
            option = listProceso[2]
        elif form.is_valid and request.POST.get('btn') == 'stop':
            option = listProceso[3]
        elif form.is_valid and request.POST.get('btn') == 'back':
            option = listProceso[4]
            velocidad += 10
        elif form.is_valid and request.POST.get('btn') == 'next':
            option = listProceso[5]
            velocidad -= 10
            if velocidad < 1:
                velocidad = 1
        elif form.is_valid and request.POST.get('btn') == 'go':
            option = listProceso[6]
            segundosObtenidos =int(request.POST.get('pi_input'))
            numeroFrames = segundosObtenidos * propertyVideo.getTotalFPS()
    

    parametros = {'option':option,'id':id,
                  'numeroFrames':numeroFrames,
                  'velocidad':velocidad,
                  'tiempoSegundosVideo':propertyVideo.getDuracionToSegundos(),
                  'tiempoDuracionVideo':propertyVideo.getDuracionEnTiempo(),
                  'fechaRegistro':image.imagen_date.strftime(settings.DATE_INPUT_FORMATS[3]),
                  'path':image.imagen_path}

    return render(request,'picture/showVideo.html',parametros)

def recordIndex(request):
    return render(request,'record/index.html')

def moveIndex(request):
    addCam = ConfiguracionAgregarCamara()
    show_list_cam_bd = addCam.find_config_show()
    idCam = 0

    if request.method == 'POST':
        form = BotonForm(request.POST)
        if form.is_valid and request.POST.get('btn') == 'seleccionar':
            idCam = request.POST.get("selectCamToShow")
    return render(request,'move/index.html',{"show_list_cam_bd":show_list_cam_bd,"idCam":idCam})

def detectPerson(request):
    addCam = ConfiguracionAgregarCamara()
    show_list_cam_bd = addCam.find_config_show()
    idCam = 0

    if request.method == 'POST':
        form = BotonForm(request.POST)
        if form.is_valid and request.POST.get('btn') == 'seleccionar':
            idCam = request.POST.get("selectCamToShow")
            
    return render(request,'move/detectPerson.html',{"show_list_cam_bd":show_list_cam_bd,"idCam":idCam})

def pictureIndex(request):
    listProceso = [0,1,2,3]

    if request.method == 'POST':
        form = BotonForm(request.POST)
        if form.is_valid and request.POST.get('btn') == 'takePicture':
            return render(request,'picture/index.html',{'proceso':listProceso[1]})
        elif form.is_valid and request.POST.get('btn') == 'takePictureRafaga':
            return render(request,'picture/index.html',{'proceso':listProceso[2]})
        elif form.is_valid and request.POST.get('btn') == 'startRecord':
            return render(request,'picture/index.html',{'mensaje':'Grabando!','proceso':listProceso[3]})
        elif form.is_valid and request.POST.get('btn') == 'stopRecord':
            return render(request,'picture/index.html',{'proceso':listProceso[0]})
        elif form.is_valid and request.POST.get('btn') == 'listPictures':
            return redirect('pictureList')
    return render(request,'picture/index.html',{'proceso':listProceso[0]})

def showPictureDirectory(request,id):
    image = get_object_or_404(Imagen, pk=id)
    worksFiles = WorksFiles()
    if request.method == 'POST':
        pathImagen = request.POST.get('btn')
        worksFiles.deleteFile(settings.STORAGE_TAKE_PICTURE,pathImagen)
    listImages = worksFiles.search_files(str(settings.STORAGE_TAKE_PICTURE)+"/"+image.imagen_path,settings.STORAGE_TAKE_PICTURE,settings.EXTENSION_IMG)
    return render(request,'picture/showDirectory.html',{'listImages':listImages,'id':id})

def listPictures(request):
    if request.method == 'POST':
        id = int(request.POST.get('btn'))
        imagen = Imagen.objects.get(id=id)
        worksFiles = WorksFiles()
        if imagen.imagen_type == 1 or imagen.imagen_type == 3:
            worksFiles.deleteFile(settings.STORAGE_TAKE_PICTURE,imagen.imagen_path)
            imagen.delete()
        elif imagen.imagen_type == 2:
            worksFiles.deleteDirectory(settings.STORAGE_TAKE_PICTURE,imagen.imagen_path)
            imagen.delete()

    listImages = Imagen.objects.all().order_by('-imagen_date')#QuerySet
    return render(request,'picture/list.html',{'listImages':listImages})

def newRecord(request):
    if request.method == 'POST':
        form  = CreateRecord(request.POST)
        if form.is_valid():
            saveRecord = form.save(commit = False)
            saveRecord.first_name = request.POST.get('first_name')
            saveRecord.last_name = request.POST.get('last_name')
            saveRecord.date_of_birth = request.POST.get('date_of_birth')
            saveRecord.rut = request.POST.get('rut')
            saveRecord.apartament = request.POST.get('apartament')
            saveRecord.level_dangerous = request.POST.get('level_dangerous')
            saveRecord.phone_number = request.POST.get('phone_number')
            saveRecord.date_register = timezone.now()
            saveRecord.image_name = saveRecord.first_name+"_"+saveRecord.last_name+"_"+str(saveRecord.rut)
            saveRecord.save()
            locationKey = saveRecord.id

            return redirect('showRecord', pk=locationKey)
    else:
        form = CreateRecord()
    return render(request,'record/new.html',{'form':form})

def showRecord(request, pk):
    totRegistPicture = 0
    count = 0
    showRecord = get_object_or_404(Record, pk=pk)
    dirUserRecord = str(settings.STORAGE_CAM_RECORD)+'/'+showRecord.image_name
    if os.path.exists(dirUserRecord):
        for path in os.listdir(dirUserRecord):
            if os.path.isfile(os.path.join(dirUserRecord, path)):
                count += 1
                totRegistPicture = int(count / 3)
    return render(request,'record/show.html', {'showRecord':showRecord,'totRegistPicture':totRegistPicture})

def takePictureRecord(request, pk):
    showRecord = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        global videoCam
        form = BotonForm(request.POST)
        if form.is_valid() and request.POST.get('btn') == 'TomarFoto' and videoCam != None:
            videoCam.deleteAPicture(showRecord)
            videoCam.takeAPicture(showRecord)
            return redirect('showRecord', pk=showRecord.id)
        elif form.is_valid() and request.POST.get('btn') == 'Voler':
            return redirect('showRecord', pk=showRecord.id)

    return render(request,'record/takePicture.html', {'showRecord':showRecord})

def takeRecord(request,pk):
    showRecord = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        form = BotonForm(request.POST)
        if form.is_valid() and request.POST.get('btn') == 'Voler':
            return redirect('showRecord', pk=showRecord.id)
    return render(request,'record/takeRecord.html',{'pk':showRecord.id})

def deleteRecord(request, pk):
    record = Record.objects.get(id=pk)
    if request.method == 'POST':
        takeRecordCam = TakeRecordCam()
        takeRecordCam.deleteRecord(record)
        camareVideoCam = VideoCam()
        camareVideoCam.deleteAPicture(record)
        record.delete()
        return redirect('showListRecord')
    return render(request,'record/delete.html', {'record': record})

def showRecordAux(request, pk):
    try:
        print("mensaje = ",pk)
        recordId = Record.objects.get(pk = pk)
    except Record.DoesNotExist:
        raise Http404("No existe REGISTRO")
    return render(
            request,
            'record/show.html',
            context={'showRecord':recordId,}
        )

def showListRecord(request):
    listReco = Record.objects.all().order_by('date_register')#QuerySet
    return render(request,'record/list.html',{'showListReco':listReco})

def execTrainRecord(request):
    if request.method == 'POST':
        form  = BotonForm(request.POST)
        if form.is_valid() and request.POST.get('btn') == 'trainRecord':
            #task = trainRecordBarLBPH.delay(10)
            task = trainRecordBarFisherFace.delay(10)
            return render(request,'record/trainRecord.html',context={'task_id': task.task_id})
    return render(request,'record/trainRecord.html')

def updateRecord(request, pk):
    showRecord = get_object_or_404(Record, pk=pk)
    if request.method == 'GET':
        context = {'form': UpdateRecord(instance=showRecord), 'id': pk}
        return render(request,'record/edit.html',context)
    elif request.method == 'POST':
        form = UpdateRecord(request.POST, instance=showRecord)
        if form.is_valid():
            form.save()
            return redirect('showRecord', pk=showRecord.id)
        else:
            return render(request,'record/edit.html',{'form':form})