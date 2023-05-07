import django_tables2 as tables
from .models import ConversationLog

class ResultTable(tables.Table):
    class Meta:
        model = ConversationLog
        fields = ('time', 'content', 'result')