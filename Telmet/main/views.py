from django.shortcuts import render
from main.models import ConversationLog
from datetime import datetime

# result DB
from main.model_control import ModelControl
from .result_table import ResultTable

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
    # model_control에 있는 함수 가져오기
    model_control = ModelControl()
    #장고 테이블
    logs = ConversationLog.objects.all()
    table = ResultTable(logs)
    context = {
                'abuse_data' : model_control.load_abuse_data(),
                'sexual_data' : model_control.load_sexual_data(),
                'abuse_count' : model_control.load_abuse_count(),
                'sexual_count' : model_control.load_sexual_count(),
                'table' : table, #장고 테이블
                }
    return render(request, 'main/result.html', context)

