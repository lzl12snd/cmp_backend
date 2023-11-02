from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import InvalidPage, Paginator
from django.http import HttpRequest
from ninja import Form, Header, Query, Body, Router

from backend.utils.auth import auth
from backend.settings import REDIS_PREFIX, get_logger
from backend.utils.response_types import Response
from user.models import User

router = Router(tags=["用户"])

logger = get_logger()


@router.get("wxa/generate/link", summary="获取小程序拉起链接")
def get_wxa_generate_urllink(
    request: HttpRequest,
    app_id: str = Query(..., description="小程序 appid"),
):
    """
    ```
    url: str 小程序链接
    ```
    """
    return Response.data({"url": "https://wxaurl.cn/pFawq35qbfd"})


@router.post("test/user/login", summary="登录(测试用)", deprecated=True)
def test_user_login(
    request: HttpRequest,
    phone: str = Body(..., regex=r"^1[0-9]{10}$"),
    password: str = Body("123456"),
):
    """
    ```
    token: str
    ```
    """
    if password != "123456":
        return Response.error("密码错误")

    user = User.get_or_create(phone=phone)
    token = auth.generate_token(user.pk)
    return Response.data({"token": token})


@router.get("user/info", auth=auth.get_auth(), summary="用户信息")
def get_user_info(request: HttpRequest):
    """
    ```
    id: int
    phone: str 手机
    credits: int 积分
    ```
    """
    user = auth.get_login_user(request)
    data = {
        "id": user.id,
        "phone": user.phone,
        "credits": user.credits,
    }
    return Response.data(data)


@router.get("user/express", auth=auth.get_auth(), summary="获取快递信息")
def get_user_express(request: HttpRequest):
    """
    ```
    express_name: str 姓名
    express_phone: str 手机
    express_area: str 地区
    express_address: str 地址
    ```
    """

    user = auth.get_login_user(request)

    data = {
        "express_name": user.express_name,
        "express_phone": user.express_phone,
        "express_area": user.express_area,
        "express_address": user.express_address,
    }
    return Response.data(data)


@router.post("user/express", auth=auth.get_auth(), summary="设置快递信息")
def post_user_express(
    request: HttpRequest,
    express_name: str = Body(..., description="姓名"),
    express_phone: str = Body(..., description="手机"),
    express_area: str = Body(..., description="地区"),
    express_address: str = Body(..., description="地址"),
):
    user = auth.get_login_user(request)

    if not all([express_name, express_phone, express_area, express_address]):
        return Response.error("请填写完整")

    user.express_name = express_name
    user.express_phone = express_phone
    user.express_area = express_area
    user.express_address = express_address
    user.save(
        update_fields=[
            "express_name",
            "express_phone",
            "express_area",
            "express_address",
        ]
    )
    return Response.ok()


@router.get("user/credits/ranking/list", summary="排行榜")
def get_user_credits_ranking_list(request: HttpRequest):
    """
    ```
    id: int
    phone: str 手机
    credits: int 积分
    ```
    """
    queryset = User.objects.order_by("-credits")[:10]
    data = []
    for i in queryset:
        data.append(
            {
                "id": i.id,
                "phone": i.phone_mask,
                "credits": i.credits,
            }
        )
    return Response.list(data)


@router.get("user/credits/ranking/all", summary="排行榜")
def get_user_credits_ranking_all(request: HttpRequest):
    """
    ```
    id: int
    phone: str 手机
    credits: int 积分
    ```
    """
    queryset = User.objects.order_by("-credits")[:10]
    data = {}
    data_a = []
    for i in queryset:
        data_a.append(
            {
                "id": i.id,
                "phone": i.phone_mask,
                "credits": i.credits,
            }
        )
    data["A"] = data_a
    data["B"] = data_a
    data["C"] = data_a
    return Response.data(data)
