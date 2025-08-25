 
from django.contrib import admin
from django.urls import path
from . import views # импортируем файл views.py из папки приложения gjangoproject

# В файле urls.py маршрутизация начинается с адреса ПРИЛОЖЕНИЯ. Например: этот файл находится в папке приложения gjangoproject и подключен глобально к urls.py всего проекта -> все адреса описанные в этом фале  УЖЕ ПО УМОЛЧАНИЮ начинаются с адреса 127.0.0.1:8000/djangoproject/

urlpatterns = [
    path('', views.index, name='djangoproject'),
]
