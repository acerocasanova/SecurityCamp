import os,cv2
from django.conf import settings
from cam.src.utils.WorksFiles import WorksFiles


class TakePictureCamp(object):

    def __init__(self):
        self.face_detection  = cv2.CascadeClassifier(os.path.join(settings.DIR_HAARCASCADES,'haarcascade_frontalface_default.xml'))
        self.cap = cv2.VideoCapture(0)
        self.writeVideo = None
        self.frame_flip = None

        savePath = os.path.join(settings.STORAGE_TAKE_PICTURE)
        if not  os.path.exists(savePath):
            os.makedirs(settings.STORAGE_TAKE_PICTURE)

    def __del__(self):
        if self.writeVideo != None:
            self.writeVideo.release()
        self.cap.release()
        cv2.destroyAllWindows()

    def getVideo(self,proceso = 0,cantPicture = 100, pathImages = None):
        count = 0
        #contador = 1
        if proceso == 3:
            print("proceoss ", proceso)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1200)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
            self.writeVideo = cv2.VideoWriter(pathImages,cv2.VideoWriter_fourcc(*'XVID'),20.0,(int(self.cap.get(3)),int(self.cap.get(4))))

        while self.cap.isOpened():
            if not self.cap.isOpened():
                print("No esta activada la camara")
                exit()
            success, frame = self.cap.read()
            if success:
                self.frame_flip = cv2.flip(frame,1)
                if proceso == 0:
                    pass
                elif proceso == 1:
                    self.savePicture(pathImages)
                    proceso = -1
                elif proceso == 2 and count < cantPicture:
                    try:
                        self.takePicture(count ,pathImages)
                        self.createProgressBar(count)
                    except Exception as e:
                        print("Warning! Error al capturar una imagen ",str(e))
                    count += 1
                elif proceso == 3:
                    #captImage  = cv2.cvtColor(self.frame_flip,cv2.COLOR_BGR2RGB)
                    self.writeVideo.write(self.frame_flip)
                else:
                    self.createProgressBar(100,"Proceso completado")

            ret, jpeg = cv2.imencode(settings.EXTENSION_IMG, self.frame_flip)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def createProgressBar(self,percentage,mensaje = 'procesando', width = 700):
        font = 1
        color = (0,255,0)
        filled_length = 0
        if percentage > -1:
            filled_length = int((width * percentage) / 100)
            mensaje = "{}% {}".format(percentage,mensaje)

        cv2.rectangle(self.frame_flip,(0,0),(filled_length,50),color, -1)
        #text_size,_ = cv2.getTextSize(text,font,1,2)[0]
        #text_x = (width - text_size) // 2
        cv2.putText(self.frame_flip,mensaje,(10,38),font,3,(255,0,0),3)

    def takePicture(self,count = 0, pathImages = None):
        nameFile = "{}_{}{}".format("TakePicture",count,settings.EXTENSION_IMG)
        pathImages = "{}/{}".format(pathImages,nameFile)
        self.savePicture(pathImages)

    def savePicture(self,pathImages):
        print("pathImages ",pathImages)
        cv2.imwrite(pathImages,self.frame_flip)