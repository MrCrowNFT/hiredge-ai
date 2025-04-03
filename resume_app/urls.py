from django.urls import path
from . import views

urlpatterns =[
    path('', views.upload_resume, name='upload_resume'),
    path('enhance/', views.enhance_resume, name='enhance_resume'),
    path('download/', views.download_resume, name='download_resume'),
]