from django.contrib import admin
from goods.models import Goods


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    pass
