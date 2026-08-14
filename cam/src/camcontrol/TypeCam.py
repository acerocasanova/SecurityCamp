

class GetTypeCam(object):
    def __init__(self):
        pass
    def get_cam_integrada(self,addCam):
        return addCam.a_channel
    
    def get_cam_ip(self,addCam):
        #"rtsp://admin:6337821Super@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0"
        cam = "rtsp://{}:{}@{}:{}/cam/realmonitor?channel={}&subtype={}".format(
            addCam.a_user,addCam.a_pass,addCam.a_ip,addCam.a_port,addCam.a_channel,addCam.a_tipo_transmision)
        return cam
    
    
