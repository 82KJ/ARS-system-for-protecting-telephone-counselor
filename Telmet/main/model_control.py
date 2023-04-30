from channels.db import database_sync_to_async
from .models import ConversationLog



class ModelControl:

    # Async Channels에서 Transaction 조작을 위해 database_sync_to_async decorator 사용

    # Insert text into ConversationLog
    @database_sync_to_async
    def insert_content(self, text):
        ConversationLog.objects.create(content=text)

    @database_sync_to_async
    def select_last_conversation(self):
        return ConversationLog.objects.last()
    
    @database_sync_to_async
    def drop_conversationlog_table(self):
        ConversationLog.objects.all().delete()

    @database_sync_to_async
    def update_result(self, id, res):
        ConversationLog.objects.filter(log_id=id).update(result=res)

    