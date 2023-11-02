# Generated by Django 3.2.22 on 2023-10-23 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=150, verbose_name='商品名称')),
                ('image', models.ImageField(upload_to='', verbose_name='商品图片')),
                ('description', models.TextField(verbose_name='商品描述')),
                ('price', models.PositiveIntegerField(verbose_name='商品价格')),
                ('inventory', models.PositiveIntegerField(verbose_name='商品库存')),
                ('inventory_total', models.PositiveIntegerField(verbose_name='商品总库存')),
                ('enable_sale_time_range', models.BooleanField(default=False, verbose_name='是否开启时间范围')),
                ('sale_time_start', models.DateTimeField(blank=True, null=True, verbose_name='开售时间')),
                ('sale_time_end', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
            ],
            options={
                'verbose_name': '商品表',
                'verbose_name_plural': '商品表',
                'db_table': 'cmp_goods',
            },
        ),
    ]
