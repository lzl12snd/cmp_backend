from django.db import models

from backend.settings import DB_PREFIX
from backend.utils.order_utils import get_goods_order_id
from backend.utils.typed_model_meta import TypedModelMeta
from goods.models import Goods
from user.models import User


class Order(models.Model):
    class OrderStatus(models.IntegerChoices):
        PENDING = 1, "待发货"
        SHIPPED = 2, "已发货"
        IN_TRANSIT = 3, "运送中"
        DELIVERED = 4, "已签收"

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name="商品")
    unit_price = models.IntegerField(default=0, verbose_name="单价")
    quantity = models.IntegerField(default=0, verbose_name="数量")
    total_price = models.IntegerField(default=0, verbose_name="总价")
    order_id = models.CharField(max_length=150, default=get_goods_order_id, verbose_name="订单号")
    status = models.SmallIntegerField(default=OrderStatus.PENDING, choices=OrderStatus.choices, verbose_name="订单状态")
    express_name = models.CharField(max_length=150, default="", verbose_name="收货人")
    express_phone = models.CharField(max_length=150, default="", verbose_name="收货手机号码")
    express_area = models.CharField(max_length=150, default="", verbose_name="所在地区")
    express_address = models.CharField(max_length=150, default="", verbose_name="详细地址")

    class Meta(TypedModelMeta):
        db_table = f"{DB_PREFIX}_order"
        verbose_name = "订单表"
        verbose_name_plural = verbose_name
        ordering = ["-id"]

    @classmethod
    def create(
        cls,
        user: User,
        goods: Goods,
        unit_price: int,
        quantity: int,
        total_price: int,
        express_name: str,
        express_phone: str,
        express_area: str,
        express_address: str,
    ) -> "Order":
        return cls.objects.create(
            user=user,
            goods=goods,
            unit_price=unit_price,
            quantity=quantity,
            total_price=total_price,
            express_name=express_name,
            express_phone=express_phone,
            express_area=express_area,
            express_address=express_address,
        )
