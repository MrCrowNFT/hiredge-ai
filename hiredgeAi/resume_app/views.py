from django.shortcuts import render, HttpResponse

# Create your views here.
#todo Here goes the request response fn
def home(request):
    return HttpResponse("hello World")