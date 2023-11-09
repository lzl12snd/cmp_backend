# Generated by Django 3.2.22 on 2023-11-08 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20231103_1850'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeiyiTreasure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '唯艺藏品表',
                'verbose_name_plural': '唯艺藏品表',
                'db_table': 'cmp_weiyi_treasure',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='level',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], default='C', max_length=100, verbose_name='等级'),
        ),
    ]
