# Generated by Django 3.2.22 on 2023-11-09 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_auto_20231108_1743'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='usercreditslog',
            name='user_credits_log_order_id_app',
        ),
        migrations.RemoveConstraint(
            model_name='weiyitreasure',
            name='weiyi_treasure_name_number',
        ),
        migrations.AddField(
            model_name='weiyitreasure',
            name='commodity_uuid',
            field=models.CharField(default='', max_length=150, verbose_name='商品唯一标识'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='usercreditslog',
            constraint=models.UniqueConstraint(fields=('order_id', 'app'), name='user_credits_log_order_app_unique'),
        ),
        migrations.AddConstraint(
            model_name='weiyitreasure',
            constraint=models.UniqueConstraint(fields=('commodity_uuid', 'number'), name='weiyi_treasure_commodity_number_unique'),
        ),
    ]