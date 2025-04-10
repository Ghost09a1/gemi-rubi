# Generated by Django 4.2.20 on 2025-04-10 16:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('my_messages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='participants',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
