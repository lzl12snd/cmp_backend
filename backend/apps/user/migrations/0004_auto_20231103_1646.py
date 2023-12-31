# Generated by Django 3.2.22 on 2023-11-03 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20231023_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.CharField(blank=True, default=None, max_length=150, null=True, verbose_name='头像'),
        ),
        migrations.AddField(
            model_name='user',
            name='weiyi_access_token',
            field=models.JSONField(default=dict, verbose_name='唯艺 access token'),
        ),
    ]
