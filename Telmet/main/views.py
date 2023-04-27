from django.shortcuts import render

def home(request):
    return render(request, 'main/home.html')

def chatroom(request):
    return render(request, 'main/chatroom.html')

def result(request):
    return render(request, 'main/result.html')