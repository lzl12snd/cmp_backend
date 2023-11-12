import datetime
from django.db.models import Q, F
from django.db import models, transaction
from backend.settings import DB_PREFIX
from backend.utils.typed_model_meta import TypedModelMeta


class Goods(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    sort = models.IntegerField(default=0, verbose_name="排序")
    name = models.CharField(max_length=150, verbose_name="商品名称")
    image = models.ImageField(verbose_name="商品图片")
    description = models.TextField(verbose_name="商品描述")
    original_price = models.PositiveIntegerField(verbose_name="商品原价")
    inventory = models.PositiveIntegerField(verbose_name="商品库存")
    inventory_total = models.PositiveIntegerField(verbose_name="商品总库存")
    status = models.BooleanField(default=False, verbose_name="商品上架")

    discount_price = models.PositiveIntegerField(verbose_name="商品折扣价格")
    discount_time_end = models.DateTimeField(verbose_name="折扣时间", null=True, blank=True)
    sale_time_end = models.DateTimeField(verbose_name="限时时间", null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def price(self):
        now = datetime.datetime.now()
        if self.discount_time_end and self.discount_time_end > now:
            return self.discount_price
        return self.original_price

    def check_props(self):
        if self.discount_time_end and self.discount_price > self.original_price:
            raise ValueError("折扣价格不能大于价格")
        if self.discount_time_end and self.sale_time_end:
            raise ValueError("折扣时间和限时时间不能同时启用")

    def change_inventory(self, quantity: int):
        with transaction.atomic():
            Goods.objects.filter(id=self.id).update(inventory=F("inventory") - quantity)
            self.refresh_from_db(fields=["inventory"])
            if self.inventory < 0:
                raise ValueError("库存不足")

    class Meta(TypedModelMeta):
        db_table = f"{DB_PREFIX}_goods"
        verbose_name = "商品表"
        verbose_name_plural = verbose_name
        ordering = ["sort", "-id"]
