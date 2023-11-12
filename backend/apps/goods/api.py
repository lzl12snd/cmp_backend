import datetime
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import InvalidPage, Paginator
from django.http import HttpRequest
from django.db.models import Q
from ninja import Form, Header, Query, Body, Router

from backend.utils.auth import auth
from backend.settings import REDIS_PREFIX, get_logger
from backend.utils.response_types import Response
from user.models import User
from goods.models import Goods

router = Router(tags=["商品"])

logger = get_logger()


@router.get("goods/list", summary="商品列表")
def get_goods_list(request: HttpRequest, page: int = Query(..., description="页码"), size: int = Query(..., description="每页数量")):
    """
    ```
    id: int 创建时间
    create_time: str 创建时间
    name: str 商品名称
    image: str 商品图片
    description: str 商品描述
    price: int 商品价格
    original_price: int 商品原价
    discount_price: int 商品折扣价格
    inventory: int 商品库存
    inventory_total: int 商品总库存
    discount_time_end: str? 折扣时间
    sale_time_end: str? 限时时间
    ```
    """
    sale_time_filter = Q(sale_time_end__isnull=True) | Q(sale_time_end__gt=datetime.datetime.now())
    queryset = Goods.objects.filter(status=True).filter(sale_time_filter)
    page_queryset = Paginator(queryset, size).page(page)
    data = []
    for i in page_queryset:
        is_discount = i.discount_time_end and i.discount_time_end > datetime.datetime.now()
        discount_time_end = i.discount_time_end if is_discount else None

        data.append(
            {
                "id": i.id,
                "create_time": i.create_time,
                "name": i.name,
                "image": i.image,
                "description": i.description,
                "original_price": i.original_price,
                "discount_price": i.discount_price,
                "price": i.price,
                "inventory": i.inventory,
                "inventory_total": i.inventory_total,
                "discount_time_end": discount_time_end,
                "sale_time_end": i.sale_time_end,
            }
        )

    return Response.paginator_list(data=data, page=page_queryset)
