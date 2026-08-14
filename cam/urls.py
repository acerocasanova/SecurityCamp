from django.urls import path, include, re_path
from cam import views

urlpatterns = [
    path('', views.index, name='index'),
    path('showVideoCam', views.showVideoCam, name='showVideoCam'),
    path('showVideoIP', views.showVideoIP, name='showVideoIP'),
    path('showVideoCamTakeRecord/<int:pk>',views.showVideoCamTakeRecord, name='showVideoCamTakeRecord'),
    path('showDetectedRecord',views.showDetectedRecord, name ='showDetectedRecord'),
    path('showDetectedMove/<int:idCam>', views.showDetectedMove, name='showDetectedMove'),
    path('showDetectedPerson/<int:idCam>', views.showDetectedPerson, name='showDetectedPerson'),
    path('showTakePicture/<int:proceso>',views.showTakePicture, name='showTakePicture'),
    path('showVideo/<int:id>/<int:option>/<int:numeroFrames>/<int:velocidad>',views.showVideo,name='showVideo'),
    path('downloadFile/<int:id>',views.downloadFile,name='downloadFile'),
    path('showAllCam/<int:idCam>',views.showAllCam,name='showAllCam'),
    #re_path(r'^showVideoCamTakeRecord/(?P<modalidad>top|new)/$', views.showVideoCamTakeRecord, name='showVideoCamTakeRecord'),
    ]

urlpatterns += [
    path('record/index', views.recordIndex, name='recordIndex'),
    path('record/showList',views.showListRecord, name ='showListRecord'),
    path('record/<int:pk>/show/', views.showRecord, name ='showRecord'),
    path('record/new', views.newRecord,name='newRecord'),
    path('record/<int:pk>/delete/', views.deleteRecord, name='deleteRecord'),
    path('record/<int:pk>/takePicture',views.takePictureRecord,name='takePictureRecord'),
    path('record/<int:pk>/takeRecord',views.takeRecord,name='takeRecord'),
    path('record/execTrainRecord',views.execTrainRecord, name='execTrainRecord'),
    path('record/<int:pk>/update',views.updateRecord,name='updateRecord'),
]

urlpatterns +=[
    path('move/index', views.moveIndex, name='moveIndex'),
    path('move/detectPerson', views.detectPerson, name='detectPerson'),
]

urlpatterns +=[
    path('picture/index', views.pictureIndex,name='pictureIndex'),
    path('picture/list', views.listPictures,name='pictureList'),
    path('picture/<int:id>/showDirectory/', views.showPictureDirectory,name='showPictureDirectory'),
    path('picture/<int:id>/showControlVideo/',views.showControlVideo,name='showControlVideo'),
]

urlpatterns +=[
    path('config/index',views.configIndex,name='configIndex'),
    path('config/<int:id>/delete',views.configDelete,name='configDelete'),
    path('config/cam', views.configCam,name='configCam'),
    path('config/<int:id>/deleteCam',views.configDeleteCam,name='configDeleteCam'),
]

urlpatterns +=[
    path('showcam/index',views.showCamIndex,name='showCamIndex'),
    path('showcam/<int:numero>/pantalla',views.show_pantalla,name='show_pantalla')
]



