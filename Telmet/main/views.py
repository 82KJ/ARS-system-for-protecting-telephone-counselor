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
    data = []
    abuse_data = []
    sexual_data = []

    conversation_log = ConversationLog.objects.all()
    for log in conversation_log:    
        data.append({'content': log.content, 'result' : log.result})
        if log.result==1 :
            abuse_data.append({'content': log.content, 'time' : log.time, 'result' : log.result})
        elif log.result==2 :
            sexual_data.append({'content': log.content, 'time' : log.time, 'result' : log.result})

    # 갯수 정보
    count = ConversationLog.objects.count()
    abuse_count = ConversationLog.objects.filter(result=1).count
    sexual_count = ConversationLog.objects.filter(result=2).count
    context = {'data': data, 
                'count': count, 
                'abuse_data' : abuse_data,
                'sexual_data' : sexual_data,
                'abuse_count' : abuse_count,
                'sexual_count' : sexual_count,
                }
    return render(request, 'main/result.html', context)

