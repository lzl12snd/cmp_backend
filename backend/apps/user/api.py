import json
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.db import transaction
from django.db.models import Sum
from ninja import Form, Header, Query, Body, Router

from backend.utils.auth import auth
from backend.settings import REDIS_PREFIX, get_logger
from backend.utils.hashid_utils import hashid_encode
from backend.utils.response_types import Response
from backend.utils.weiyi.treasure_api import get_user_treasure
from user.models import User, UserCreditsLog, UserWeiyiTreasure, WeiyiTreasureInfo
from backend.utils.weiyi import weiyi_client

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


@router.get("weiyi/oauth2/authorize", summary="weiyi oauth2 authorize")
def get_weiyi_oauth2_authorize(
    request: HttpRequest,
    debug: bool = Query(False),
):
    """
    url: str
    """
    url = weiyi_client.get_authorization_url(debug)
    return Response.data({"url": url})


@router.get("weiyi/oauth2/callback", summary="weiyi oauth2 callback")
def get_weiyi_oauth2_callback(
    request: HttpRequest,
):
    """
    token: str
    """
    error = request.GET.get("error")
    if error:
        logger.info(error)
        return Response.error(error)
    code = request.GET.get("code")
    if not code:
        return Response.error("缺少code")

    token = weiyi_client.get_access_token(code)
    user_info = weiyi_client.get_user_base_info(access_token=token.accessToken)

    user = User.get_or_create(phone=user_info.phone, avatar=user_info.avatar)
    user.save_weiyi_token(token)
    token = auth.generate_token(user.phone)
    return Response.data({"token": token})


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
    token = auth.generate_token(user.phone)
    return Response.data({"token": token})


@router.get("user/info", auth=auth.get_auth(), summary="用户信息")
def get_user_info(request: HttpRequest):
    """
    ```
    id: int
    phone: str 手机
    credits: int 积分
    avatar: str 头像
    is_whitelist: bool 是否是白名单
    user_type: "A" | "B" | "C" 等级
    rank: int 所在等级排行
    total_income: int 总收入
    invite_parent: str? 邀请人手机号
    be_invited_code: str? 邀请人邀请码
    invited_num: str 邀请数量
    invite_code: str 邀请码
    ```
    """
    user = auth.get_login_user(request)

    is_whitelist = (
        UserWeiyiTreasure.objects.filter(
            commodity_uuid__in=WeiyiTreasureInfo.objects.filter(
                is_whitelist=True,
            ).values_list("commodity_uuid")
        )
        .values_list("user", flat=True)
        .filter(user=user)
        .exists()
    )

    rank = User.objects.filter(level=user.level, credits__gte=user.credits).count()
    total_income = sum(
        UserCreditsLog.objects.filter(
            user=user,
            operation=1,
        )
        .aggregate(value__sum=Sum("value"))
        .values()
    )
    invited_num = User.objects.filter(parent=user).count()

    data = {
        "id": user.id,
        "phone": user.phone,
        "avatar": user.avatar,
        "credits": user.credits,
        "is_whitelist": is_whitelist,
        "user_type": user.level,
        "rank": rank,
        "total_income": total_income,
        "invite_parent": user.parent.phone_mask if user.parent else None,
        "be_invited_code": hashid_encode(user.parent.id) if user.parent else None,
        "invited_num": invited_num,
        "invite_code": hashid_encode(user.id),
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


@router.get("user/credits/ranking/all", summary="排行榜")
def get_user_credits_ranking_all(request: HttpRequest):
    """
    ```
    id: int
    phone: str 手机
    credits: int 积分
    ```
    """
    levels = [User.LevelChoice.A, User.LevelChoice.B, User.LevelChoice.C]
    querysets = [User.objects.filter(level=level).order_by("-credits")[:10] for level in levels]
    datas = [
        [
            {
                "id": i.id,
                "phone": i.phone_mask,
                "credits": i.credits,
            }
            for i in queryset
        ]
        for queryset in querysets
    ]
    data = dict(zip(levels, datas))
    return Response.data(data)


@router.post("user/weiyi/check", auth=auth.get_auth(), summary="唯艺藏品同步")
def post_user_weiyi_check(
    request: HttpRequest,
):
    user = auth.get_login_user(request)
    treasures = get_user_treasure(user.phone)
    logger.info(f"treasures {len(treasures)}")
    with transaction.atomic():
        for i in treasures:
            UserWeiyiTreasure.update_or_create(
                user=user,
                commodity_uuid=i.commodityUuid,
                number=i.number,
                name=i.name,
                cover=i.cover,
                type_market=i.typeMarket,
            )
    return Response.ok()
