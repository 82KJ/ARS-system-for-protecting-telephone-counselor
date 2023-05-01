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
    abuse_count = ConversationLog.objects.filter(result=1).count
    sexual_count = ConversationLog.objects.filter(result=2).count
    for log in conversation_log:    
        data.append({'content': log.content, 'result' : log.result})
    context = {'data': data, 
                'count': count, 
                'abuse_count' : abuse_count,
                'sexual_count' : sexual_count
                }
    return render(request, 'main/result.html', context)

