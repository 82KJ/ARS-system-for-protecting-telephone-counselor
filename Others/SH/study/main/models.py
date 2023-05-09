from django.db import models

# Create your models here.

class Detection(models.Model):
    #분류 order
    #욕설 탐지 시각 detect_time
    #욕설 탐지 분류 result
    #욕서 탐지 내역 content
    
    order = models.CharField(max_length = 200) 
    detect_date = models.DateTimeField()   
    result = models.CharField(max_length = 15)   
    content = models.TextField()
