from django.db import models

from backend.settings import DB_PREFIX
from backend.utils.order_utils import get_goods_order_id
from backend.utils.typed_model_meta import TypedModelMeta
from goods.models import Goods
from user.models import User


class Order(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品")
    unit_price = models.IntegerField(default=0, verbose_name="单价")
    quantity = models.IntegerField(default=0, verbose_name="数量")
    total_price = models.IntegerField(default=0, verbose_name="总价")
    order_id = models.CharField(max_length=150, default=get_goods_order_id, verbose_name="订单号")
    express_name = models.CharField(max_length=150, default="", verbose_name="收货人")
    express_phone = models.CharField(max_length=150, default="", verbose_name="收货手机号码")
    express_area = models.CharField(max_length=150, default="", verbose_name="所在地区")
    express_address = models.CharField(max_length=150, default="", verbose_name="详细地址")

    class Meta(TypedModelMeta):
        db_table = f"{DB_PREFIX}_order"
        verbose_name = "订单表"
        verbose_name_plural = verbose_name
