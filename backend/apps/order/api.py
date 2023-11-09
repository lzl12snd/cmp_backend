import datetime
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import InvalidPage, Paginator
from django.http import HttpRequest
from django.db.models import Q, F
from django.db import transaction
from ninja import Form, Header, Query, Body, Router

from backend.utils.auth import auth
from backend.settings import REDIS_PREFIX, get_logger
from backend.utils.response_types import Response
from goods.models import Goods
from openapi.models import OpenApp
from user.models import User
from order.models import Order
from backend.utils.auth import auth

router = Router(tags=["商品"])

logger = get_logger()


@router.post("order/create", auth=auth.get_auth(), summary="下单")
def post_order_create(
    request: HttpRequest,
    goods_id: int = Body(..., ge=1, description="商品id"),
    quantity: int = Body(..., ge=1, description="数量"),
):
    user = auth.get_login_user(request)

    with transaction.atomic():
        goods = Goods.objects.filter(id=goods_id).first()
        if goods is None:
            return Response.error("积分不足")
        unit_price = goods.price
        total_price = unit_price * quantity
        order = Order.create(
            user=user,
            goods=goods,
            unit_price=unit_price,
            quantity=quantity,
            total_price=total_price,
        )
        user.change_credits_and_log(
            order_id=order.order_id,
            operation=-1,
            value=total_price,
            channel="商城兑换",
            app=OpenApp.objects.get(app_id="mall"),
        )
        goods.change_inventory(quantity=quantity)

    return Response.ok()


@router.get("order/list", auth=auth.get_auth(), summary="订单列表")
def get_order_list(
    request: HttpRequest,
    page: int = Query(..., description="页码"),
    size: int = Query(..., description="每页数量"),
):
    """
    ```
    id: int
    image: str
    name: str
    create_time: str
    total_price: str
    quantity: str
    status: int 1待发货; 2已发货; 3运送中; 4已签收
    ```
    """
    user = auth.get_login_user(request)
    data = []

    queryset = Order.objects.filter(user=user).order_by("-id")
    page_queryset = Paginator(queryset, size).page(page)
    for i in page_queryset:
        data.append(
            {
                "id": i.id,
                "image": i.goods.image,
                "name": i.goods.name,
                "create_time": i.create_time.date(),
                "total_price": i.total_price,
                "quantity": i.quantity,
                "status": i.status,
            }
        )
    return Response.paginator_list(data=data, page=page_queryset)


@router.get("global/order/list", summary="全局订单列表")
def get_global_order_list(
    request: HttpRequest,
):
    """
    ```
    id: int
    name: str
    phone: str
    ```
    """
    data = []
    queryset = Order.objects.order_by("-id").select_related("goods", "user").only("goods__name", "user__phone")[:10]
    for i in queryset:
        data.append(
            {
                "id": i.id,
                "name": i.goods.name,
                "phone": i.user.phone_mask,
            }
        )
    return Response.list(data=data)
