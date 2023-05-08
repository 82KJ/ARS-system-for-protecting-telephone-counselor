from django.shortcuts import render
from main.models import ConversationLog
from datetime import datetime

from main.model_control import ModelControl
from .make_table import ResultTable

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
    # DB Access 객체 만들기
    model_control = ModelControl()

    # 전체 record time
    record_time = model_control.get_total_time()

    # 조건별 대화 문장 수
    total_count = model_control.get_total_conversation_count()
    normal_count = model_control.get_normal_conversation_count()
    abuse_count = model_control.get_abuse_conversation_count()
    sexual_count = model_control.get_sexual_conversation_count()

    # 강제 종료 여부
    is_shutdown = model_control.is_shutdown()

    # 결과 테이블
    result_table = ResultTable().get_table()

    context = {
                'record_time' : str(record_time),
                'total_count' : total_count,
                'normal_count' : normal_count,
                'abuse_count' : abuse_count,
                'sexual_count' : sexual_count,
                'is_shutdown' : is_shutdown,
                'result_table' : result_table
                }
    return render(request, 'main/result.html', context)

