
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader




def hello_world(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render())


