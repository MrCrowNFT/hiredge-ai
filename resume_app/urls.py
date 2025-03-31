from django.urls import path
from . import views

urlpatterns =[
    path("", views.home, name="home")#on the route of webpage, connect to view.home , make sure is home fn
]