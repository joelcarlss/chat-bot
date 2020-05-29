from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

from django.http import HttpResponse


@csrf_exempt
def index(request):
    form = ""
    if request.method == "POST":
        form = "POST"
    # do something if form is valid
    context = {
        'form': form
    }
    return render(context)