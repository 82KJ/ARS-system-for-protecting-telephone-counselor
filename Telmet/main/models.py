from django.db import models

# Dictionary Class
# 각 사전에 대한 Table은 구현의 편의를 위해 분리 진행
# morpheme = 형태소

class AbuseDictionary(models.Model):
    morpheme = models.TextField(primary_key=True)

    def __str__(self):
        return self.morpheme
    
    class Meta:
        verbose_name='Abuse Dictionary'
        verbose_name_plural = 'Abuse Dictionary' 

class SexualDictionary(models.Model):
    morpheme = models.TextField(primary_key = True)

    def __str__(self):
        return self.morpheme
    
    class Meta:
        verbose_name = 'Sexual Dictionary'
        verbose_name_plural = 'Sexual Dictionary' 

class CounselorDictionary(models.Model):
    morpheme = models.TextField(primary_key=True)

    def __str__(self):
        return self.morpheme
    
    class Meta:
        verbose_name = 'Counselor Dictionary'
        verbose_name_plural = 'Counselor Dictionary' 

class ConversationLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    content = models.TextField(blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    result = models.IntegerField(blank=True, null=True, default=0) #공백허용

    def __str__(self):
        return self.content
    
    class Meta:
        verbose_name = 'Conversation Log'
        verbose_name_plural = 'Conversation Log'

class RecordStartTime(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now_add=True)