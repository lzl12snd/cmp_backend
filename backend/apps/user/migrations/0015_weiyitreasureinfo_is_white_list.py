# Generated by Django 3.2.22 on 2023-11-09 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_user_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='weiyitreasureinfo',
            name='is_white_list',
            field=models.BooleanField(default=False, verbose_name='是否是白名单'),
        ),
    ]
