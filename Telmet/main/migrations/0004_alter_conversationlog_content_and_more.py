# Generated by Django 4.1.7 on 2023-04-28 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_alter_conversationlog_log_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversationlog",
            name="content",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="conversationlog",
            name="result",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
