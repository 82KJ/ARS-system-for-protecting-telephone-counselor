from django.shortcuts import render
from main.models import ConversationLog
from datetime import datetime

def home(request):
    return render(request, 'main/home.html')

def chatroom(request):
    res = {}

    # 현재 시간 처리 진행
    now = datetime.now()

    date = str(now.date())
    weekdays = ['MON', 'TUE', 'WEN', 'THR', 'FRI', 'SAT', 'SUN']
    day_of_week = weekdays[now.weekday()]
    time = str(now.time())[:-7]

    cur_time = date + " " + day_of_week + " " + time
    res['cur_time'] = cur_time
    
    return render(request, 'main/chatroom.html', res)

def result(request):
    return render(request, 'main/result.html')

