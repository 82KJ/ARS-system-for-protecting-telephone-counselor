from django.contrib import admin
from .models import AbuseDictionary, SexualDictionary, CounselorDictionary

# Dictionary 등록 
admin.site.register(AbuseDictionary)
admin.site.register(SexualDictionary)
admin.site.register(CounselorDictionary)


