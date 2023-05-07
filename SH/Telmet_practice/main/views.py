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

    # 전체 record time 받아오기
    record_time = model_control.get_total_time()

    # 조건별 대화 문장 수 받아오기
    total_count = model_control.get_total_conversation_count()
    normal_count = model_control.get_normal_conversation_count()
    abuse_count = model_control.get_abuse_conversation_count()
    sexual_count = model_control.get_sexual_conversation_count()

    #장고 테이블
    logs = ConversationLog.objects.all()
    table = ResultTable(logs)
    context = {
                'record_time' : str(record_time),
                'total_count' : total_count,
                'normal_count' : normal_count,
                'abuse_count' : abuse_count,
                'sexual_count' : sexual_count,
                'abuse_data' : model_control.load_abuse_data(),
                'sexual_data' : model_control.load_sexual_data(),
                'table' : table, #장고 테이블
                }
    return render(request, 'main/result.html', context)

