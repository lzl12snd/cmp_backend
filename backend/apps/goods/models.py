from django.db import models
from backend.settings import DB_PREFIX
from backend.utils.typed_model_meta import TypedModelMeta


class Goods(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    name = models.CharField(max_length=150, verbose_name="商品名称")
    image = models.ImageField(verbose_name="商品图片")
    description = models.TextField(verbose_name="商品描述")
    price = models.PositiveIntegerField(verbose_name="商品价格")
    inventory = models.PositiveIntegerField(verbose_name="商品库存")
    inventory_total = models.PositiveIntegerField(verbose_name="商品总库存")
    status = models.BooleanField(default=False, verbose_name="商品上架")
    enable_sale_time_range = models.BooleanField(default=False, verbose_name="是否开启时间范围")
    sale_time_start = models.DateTimeField(verbose_name="开售时间", null=True, blank=True)
    sale_time_end = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta(TypedModelMeta):
        db_table = f"{DB_PREFIX}_goods"
        verbose_name = "商品表"
        verbose_name_plural = verbose_name
