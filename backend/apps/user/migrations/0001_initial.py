# Generated by Django 3.2.22 on 2023-10-20 10:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('openapi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('phone', models.CharField(max_length=150, unique=True, verbose_name='手机号')),
            ],
            options={
                'verbose_name': '用户表',
                'verbose_name_plural': '用户表',
                'db_table': 'cmp_user',
            },
        ),
        migrations.CreateModel(
            name='UserCreditsLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('value', models.IntegerField(default=0, verbose_name='操作积分数值')),
                ('operation', models.IntegerField(choices=[(1, '增加'), (-1, '减少')], verbose_name='操作')),
                ('channel', models.CharField(blank=True, default='', max_length=150, verbose_name='渠道')),
                ('app', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='openapi.openapp', verbose_name='应用')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户积分记录',
                'verbose_name_plural': '用户积分记录',
                'db_table': 'cmp_user_credits_log',
            },
        ),
    ]
