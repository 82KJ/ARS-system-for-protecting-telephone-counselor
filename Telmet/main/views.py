from django.shortcuts import render
from main.models import ConversationLog

def home(request):
    return render(request, 'main/home.html')

def chatroom(request):
    return render(request, 'main/chatroom.html')

def result(request):
    data = []
    conversation_log = ConversationLog.objects.all()
    count = ConversationLog.objects.count()
    #objects.count 바꿔야함.
    abuse_count = ConversationLog.objects.count()
    sexual_count = ConversationLog.objects.count()
    for log in conversation_log:
        data.append({'content': log.content, 'result' : log.result})
    context = {'data': data, 
                'count': count, 
                'abuse_count' : abuse_count,
                'sexual_count' : sexual_count
                }
    return render(request, 'main/result.html', context)

