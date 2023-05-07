from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'), 
    path('chatroom', views.chatroom, name='chatroom'),
    path('result',views.result, name='result')
]