from typing import Literal
from django.core.paginator import Paginator
from django.http import HttpRequest
from ninja import Form, Header, Query, Body, Router

from backend.settings import REDIS_PREFIX, get_logger
from backend.utils.auth import auth_admin
from backend.utils.response_types import Response
from openapi.models import OpenApp
from user.models import User, UserCreditsLog

router = Router(tags=["用户"])

logger = get_logger()

from ninja.security import HttpBasicAuth


class OpenAppAuth(HttpBasicAuth):
    def authenticate(self, request: HttpRequest, username: str, password: str):
        referer = request.headers.get("referer", "")
        if "servicewechat" in referer:
            raise ValueError("接口应在服务器端调用")
        user_agent = request.headers.get("User-Agent", "")
        if "UnityPlayer" in user_agent:
            raise ValueError("接口应在服务器端调用")
        user = OpenApp.objects.filter(app_id=username, app_secret=password).only("id").first()
        if user is None:
            return None
        return user.id


def get_login_openapp(request: HttpRequest):
    _id = getattr(request, "auth", None)
    return OpenApp.objects.get(id=_id)


@router.get("ping", auth=OpenAppAuth(), summary="测试")
def get_ping(request: HttpRequest):
    app = get_login_openapp(request)
    return Response.data({"pong": app.name})


@router.post("user/credits", auth=OpenAppAuth(), summary="修改用户积分")
def post_user_credits(
    request: HttpRequest,
    phone: str = Body(..., regex=r"^1[0-9]{10}$", description="手机号"),
    value: int = Body(..., gt=0, description="积分"),
    channel: str = Body(..., max_length=150, description="渠道(变动原因)"),
    operation: Literal[1, -1] = Body(..., description="操作 1增加 -1减少"),
    order_id: str = Body(..., max_length=150, description="订单号 每个app_id需要唯一"),
):
    """
    ```
    可能因积分不足减少失败
    ```
    """
    app = get_login_openapp(request)
    user = User.get_or_create(phone=phone)
    user.change_credits_and_log(
        order_id=order_id,
        operation=operation,
        value=value,
        channel=channel,
        app=app,
    )
    return Response.ok()


@router.get("user/credits", auth=OpenAppAuth(), summary="获取用户积分")
def get_user_credits(
    request: HttpRequest,
    phone: str = Query(..., regex=r"^1[0-9]{10}$", description="手机号"),
):
    """
    响应参数
    ```
    credits: int 积分
    ```
    """
    user = User.objects.filter(phone=phone).first()
    credits = user.credits if user else 0
    return Response.data({"credits": credits})


@router.get("user/credits/log/list", auth=OpenAppAuth(), summary="获取用户积分记录")
def get_user_credits_list(
    request: HttpRequest,
    phone: str = Query(..., regex=r"^1[0-9]{10}$", description="手机号"),
    page: int = Query(..., ge=1, description="页码"),
    size: int = Query(..., ge=1, le=1000, description="每页数量"),
):
    """
    data 数组 响应参数
    ```
    create_time: str 创建时间
    order_id: str 订单号
    value: int 操作积分数值
    operation: int 操作 1增加 -1减少
    channel: str 渠道(变动原因)
    ```
    """
    app = get_login_openapp(request)
    user = User.objects.filter(phone=phone).first()
    if not user:
        return Response.page_list(data=[], total=0, total_page=1)

    queryset = UserCreditsLog.objects.filter(user=user, app=app).order_by("-id")
    page_queryset = Paginator(queryset, size).page(page)

    data = []
    for i in page_queryset:
        data.append(
            {
                "create_time": i.create_time,
                "order_id": i.order_id,
                "value": i.value,
                "operation": i.operation,
                "channel": i.channel,
            }
        )

    return Response.paginator_list(data=data, page=page_queryset)
