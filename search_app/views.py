from django.shortcuts import render, redirect, reverse, get_object_or_404


def base(request):
    return render(request, "base.html")

def index(request):
    return render(request, "index.html")    

def services(request):
    return render(request, "services.html")

def about(request):
    return render(request, "about.html")


# Create your views here.

def chat(request):
    return render(request, "chat.html")