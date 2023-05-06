from channels.db import database_sync_to_async
from .models import ConversationLog, RecordStartTime
from .models import AbuseDictionary, SexualDictionary, CounselorDictionary

class ModelControl:

    # Async Channels에서 Transaction 조작을 위해 database_sync_to_async decorator 사용

    # RecordStartTime CRUD
    @database_sync_to_async
    def insert_record_time(self):
        RecordStartTime.objects.create()

    @database_sync_to_async
    def drop_recordstarttime_table(self):
        RecordStartTime.objects.all().delete()

    def select_start_time(self):
        RecordStartTime.objects.first()

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
    
    # result DB
    def load_abuse_data(self):
        abuse_data = []
        conversation_log = ConversationLog.objects.all()
        for log in conversation_log:
            if log.result==1 :
                abuse_data.append({'content': log.content, 'time' : log.time, 'result' : log.result})
        return abuse_data
    
    def load_sexual_data(self):
        sexual_data = []
        conversation_log = ConversationLog.objects.all()
        for log in conversation_log:
            if log.result==2 :
                sexual_data.append({'content': log.content, 'time' : log.time, 'result' : log.result})
        return sexual_data

    def load_abuse_count(self):
        return ConversationLog.objects.filter(result=1).count
    
    def load_sexual_count(self):
        return ConversationLog.objects.filter(result=2).count
    
    def get_total_time(self):
        first_record_time = RecordStartTime.objects.first()
        last_conversation = ConversationLog.objects.last()

        if first_record_time is None or last_conversation is None:
            return 0
        else:
            delta_time = last_conversation.time - first_record_time.time
            return delta_time.seconds