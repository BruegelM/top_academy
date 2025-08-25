from django.shortcuts import render
# генерация стандартного HTTP ответа
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
# Create your views here.
