# Generated by Django 3.2.22 on 2023-11-09 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_weiyitreasure_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weiyitreasure',
            name='cover',
            field=models.CharField(max_length=1024, verbose_name='图片'),
        ),
    ]