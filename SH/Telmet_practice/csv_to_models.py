import csv
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Telmet.settings")
django.setup()

from main.models import AbuseDictionary, SexualDictionary, CounselorDictionary

AbuseDictionary.objects.all().delete()
with open('폭언사전.csv', encoding='utf-8') as csv_file:
    rows = csv.reader(csv_file)
    next(rows, None)
    for row in rows:
        AbuseDictionary.objects.create(
            morpheme = row[1]
        )
        print(row)


SexualDictionary.objects.all().delete()
with open('성희롱사전.csv', encoding='utf-8') as csv_file:
    rows = csv.reader(csv_file)
    next(rows, None)
    for row in rows:
        SexualDictionary.objects.create(
            morpheme = row[1]
        )
        print(row)

CounselorDictionary.objects.all().delete()
with open('상담원사전.csv', encoding='utf-8') as csv_file:
    rows = csv.reader(csv_file)
    next(rows, None)
    for row in rows:
        CounselorDictionary.objects.create(
            morpheme = row[1]
        )
        print(row)



