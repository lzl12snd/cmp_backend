# Generated by Django 3.2.22 on 2023-10-23 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='status',
            field=models.BooleanField(default=False, verbose_name='商品上架'),
        ),
    ]