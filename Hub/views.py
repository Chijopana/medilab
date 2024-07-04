from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def hub(request):
    return render(request,'Hub/main_hub.html')

def login(request):
    return render(request,'Hub/login.html')

def logout(request):
    logout(request)
    return redirect('login')