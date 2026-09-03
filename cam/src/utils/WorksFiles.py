import os, shutil, time
from pathlib import Path
from django.conf import settings
from datetime import datetime
import base64

class WorksFiles(object):

    def __init__(self):
        pass
    def __del__(self):
        pass

    def deleteDirectory(self,directory,path):
        path_delete = os.path.join(str(directory)+str(path))
        try:
            if os.path.exists(path_delete):
                shutil.rmtree(path_delete)
        except Exception as e:
            print("Warning! Error ",str(e))

    def get_List_Images(self,directory,ext):
        return self.search_files(directory,'*{}'.format(ext))

    def deleteFile(self,directory,file):
        if os.path.isfile(str(directory)+str(file)):
            os.remove(str(directory)+str(file))

    def search_files_fullPath(self,directory, extensiones):
        listFile = []
        # Recorremos todos los ficheros del directorio
        for file in os.listdir(directory):
            # En directory tenemos el path y en file el nombre del fichero
            full_path = os.path.join(directory, file)
            # Si es un directorio lo que encontramos volvemos hacer la llamada
            # a la funcion para recorrer el nuevo directorio
            if os.path.isdir(full_path):
                listFile.extend(self.search_files(full_path, extensiones))
            else:
            # Sino escribimos por pantalla la ruta/fichero.
                for extension in extensiones:
                    if full_path.endswith(extension):
                        print(full_path)
                        listFile.append(full_path)
                        break
        return listFile
    
    def search_files(self,directory,directoryAux, extensiones):
        listFile = []
        urlFinal = None
        # Recorremos todos los ficheros del directorio
        for file in os.listdir(directory):
            
            # En directory tenemos el path y en file el nombre del fichero
            full_path = os.path.join(directory, file)
            # Si es un directorio lo que encontramos volvemos hacer la llamada
            # a la funcion para recorrer el nuevo directorio
            if os.path.isdir(full_path):
                listFile.extend(self.search_files(full_path,directoryAux, extensiones))
            else:
            # Sino escribimos por pantalla la ruta/fichero.
                for extension in extensiones:
                    if full_path.endswith(extension):
                        urlFinal = full_path.replace(str(directoryAux),"")
                        listFile.append(urlFinal)
                        break
        return listFile
    
    def convPath(self,full_path,directory):
        """
        Convierte una ruta de archivo real en la ruta relativa que se
        guarda en la base de datos (imagen_path) y con la que despues se
        arman URLs. Le quita el prefijo `directory` y normaliza los
        separadores a '/': en Windows, os.path.join() (usado por
        createDirectoryYMD y compania) mete '\\' entre el directorio base
        y la subcarpeta, y esa '\\' quedaba colada en la URL final
        (ej: /media/picture/take\\2026/09/02/...) porque nunca se
        normalizaba. Una URL nunca deberia llevar '\\'.
        """
        relative = str(full_path).replace(str(directory),"")
        return relative.replace("\\", "/")
    
    def createDirectoryYMD(self,direcotryBase):
        today = datetime.now()
        nameDire = today.strftime(settings.DATE_INPUT_FORMATS[0])
        savePath = os.path.join(direcotryBase,nameDire)
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        return savePath
    
    def createDirectoryYMD_HMS(self,direcotryBase):
        today = datetime.now()
        nameDire = today.strftime(settings.DATE_INPUT_FORMATS[1])
        savePath = os.path.join(direcotryBase,nameDire)
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        return savePath
    
    def createDirectoryNanoSegundos(self,direcotryBase):
        today = datetime.now()
        nameDire = today.strftime(settings.DATE_INPUT_FORMATS[1])
        nameDire = nameDire+"_"+str(time.time())
        savePath = os.path.join(direcotryBase,nameDire)
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        return savePath
    
    def fileToBase64(self,path):
        file_base64 = None
        with open(path, "rb") as f:
            file_base64 = base64.b64encode(f.read())
        return file_base64