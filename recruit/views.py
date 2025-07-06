import os
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings


def health_check(request):
    data = {'message': 'OK'}
    return JsonResponse(status=200, data=data)

def index(request):
    return render(request, 'index.html')