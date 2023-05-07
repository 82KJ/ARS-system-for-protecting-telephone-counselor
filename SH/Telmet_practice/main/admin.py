from django.contrib import admin
from .models import AbuseDictionary, SexualDictionary, CounselorDictionary
from .models import ConversationLog


# Dictionary 등록 
admin.site.register(AbuseDictionary)
admin.site.register(SexualDictionary)
admin.site.register(CounselorDictionary)

# ConversationLog 등록
admin.site.register(ConversationLog)


