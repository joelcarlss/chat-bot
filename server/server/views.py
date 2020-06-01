from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

from django.http import JsonResponse


@csrf_exempt
def index(request):
    context = {
        'form': 'data',
        'name': 'joel'
    }
    return render(request, "home.html", context)
    # return JsonResponse(request)
