from channels.db import database_sync_to_async
from .models import ConversationLog
from .models import AbuseDictionary, SexualDictionary, CounselorDictionary

class ModelControl:

    # Async Channels에서 Transaction 조작을 위해 database_sync_to_async decorator 사용

    # ConversationLog CRUD
    @database_sync_to_async
    def insert_content(self, text):
        ConversationLog.objects.create(content=text)

    @database_sync_to_async
    def select_lastest_conversation(self):
        return ConversationLog.objects.last()
    
    @database_sync_to_async
    def drop_conversationlog_table(self):
        ConversationLog.objects.all().delete()

    @database_sync_to_async
    def update_result(self, id, res):
        ConversationLog.objects.filter(log_id=id).update(result=res)

    @database_sync_to_async
    def select_conversation(self,id):
        return ConversationLog.objects.filter(log_id=id).last()
    
    @database_sync_to_async
    def id_in_conversation(self,id):
        return ConversationLog.objects.filter(log_id=id).exists()

    # Dictionary CRUD
    @database_sync_to_async
    def morph_in_abusedict(self, morph):
        return AbuseDictionary.objects.filter(morpheme=morph).exists()
    
    @database_sync_to_async
    def morph_in_sexualdict(self, morph):
        return SexualDictionary.objects.filter(morpheme=morph).exists()
    
    @database_sync_to_async
    def morph_in_counselordict(self, morph):
        return CounselorDictionary.objects.filter(morpheme=morph).exists()
    