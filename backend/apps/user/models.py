import datetime
from django.db import models, transaction
from django.db.models import F
from typing import TYPE_CHECKING, Literal, TypedDict
from backend.settings import DB_PREFIX
from backend.utils.typed_model_meta import TypedModelMeta
from openapi.models import OpenApp

from backend.utils.weiyi.models import AccessTokenData, UserCollectionListData, UserInfo
from backend.utils.weiyi import weiyi_client
from ninja.errors import AuthenticationError


class WeiyiClientUser:
    def __init__(self, user: "User"):
        self.user = user
        if not isinstance(self.user.weiyi_token, dict):
            raise AuthenticationError()
        self.token = AccessTokenData.parse_obj(self.user.weiyi_token)

    def __get_access_token(self):
        now = datetime.datetime.now()
        expire_at = self.user.weiyi_token_expire_at or now
        ttl = (expire_at - now).total_seconds()

        if ttl <= 30:
            self.token = weiyi_client.refresh_token(self.token.refreshToken)
            self.user.save_weiyi_token(self.token)

        return self.token.accessToken

    def get_user_base_info(self) -> UserInfo:
        return weiyi_client.get_user_base_info(
            access_token=self.__get_access_token(),
        )

    def get_user_position_list(self, page: int, page_size: int) -> UserCollectionListData:
        return weiyi_client.get_user_position_list(
            page=page,
            page_size=page_size,
            access_token=self.__get_access_token(),
        )


if TYPE_CHECKING:
    UserSelfForeignKey = models.ForeignKey["User" | None]
else:
    UserSelfForeignKey = models.ForeignKey


class User(models.Model):
    class LevelChoice(models.TextChoices):
        A = "A"
        B = "B"
        C = "C"

    level = models.CharField(default=LevelChoice.C, max_length=100, choices=LevelChoice.choices, verbose_name="等级")
    parent: UserSelfForeignKey = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    phone = models.CharField(max_length=150, unique=True, verbose_name="手机号")
    avatar = models.CharField(max_length=150, default=None, null=True, blank=True, verbose_name="头像")
    credits = models.BigIntegerField(default=0, verbose_name="积分")

    weiyi_token = models.JSONField(default=None, null=True, blank=True, verbose_name="唯艺 access token")
    weiyi_token_expire_at = models.DateTimeField(default=None, null=True, blank=True, verbose_name="唯艺 access token 过期时间")

    express_name = models.CharField(max_length=150, default="", verbose_name="收货人")
    express_phone = models.CharField(max_length=150, default="", verbose_name="收货手机号码")
    express_area = models.CharField(max_length=150, default="", verbose_name="所在地区")
    express_address = models.CharField(max_length=150, default="", verbose_name="详细地址")

    def __str__(self):
        return self.phone

    @property
    def parent_parent(self):
        if self.parent is None:
            return None
        return self.parent.parent

    @property
    def phone_mask(self):
        return self.phone[:3] + "****" + self.phone[-4:]

    @property
    def weiyi_client(self):
        return WeiyiClientUser(self)

    def save_weiyi_token(
        self,
        token: AccessTokenData,
    ):
        self.weiyi_token = token.dict()
        self.weiyi_token_expire_at = datetime.datetime.now() + datetime.timedelta(seconds=token.expires)
        self.save(update_fields=["weiyi_token", "weiyi_token_expire_at"])

    @classmethod
    def get_or_create(cls, phone: str, avatar: str | None = None):
        user, _ = cls.objects.get_or_create(phone=phone)
        if avatar and user.avatar != avatar:
            user.avatar = avatar
            user.save(update_fields=["avatar"])
        return user

    def can_express(self) -> bool:
        return all(
            [
                self.express_name,
                self.express_phone,
                self.express_area,
                self.express_address,
            ]
        )

    def change_credits_and_log(
        self,
        order_id: str,
        operation: Literal[1, -1],
        value: int,
        channel: str,
        app: OpenApp,
    ):
        order_exist = UserCreditsLog.objects.filter(app=app, order_id=order_id).count()
        if order_exist:
            raise ValueError("订单号重复")
        value = abs(value)
        with transaction.atomic():
            User.objects.select_for_update().filter(id=self.id).update(credits=F("credits") + (operation * value))
            self.refresh_from_db(fields=["credits"])
            if self.credits < 0:
                raise ValueError("积分不足")
            UserCreditsLog.create(
                order_id=order_id,
                user=self,
                operation=operation,
                value=value,
                channel=channel,
                app=app,
            )

    class Meta(TypedModelMeta):
        db_table = f"{DB_PREFIX}_user"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name


class UserCreditsLog(models.Model):
    class OperationChoice(models.IntegerChoices):
        INCREASE = 1, "增加"
        DECREASE = -1, "减少"

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    order_id = models.CharField(max_length=150, db_index=True, verbose_name="订单号")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    value = models.IntegerField(default=0, verbose_name="操作积分数值")
    operation = models.IntegerField(verbose_name="操作", choices=OperationChoice.choices)
    channel = models.CharField(max_length=150, default="", blank=True, verbose_name="渠道")
    app = models.ForeignKey(OpenApp, on_delete=models.CASCADE, verbose_name="应用")

    @classmethod
    def create(
        cls,
        order_id: str,
        user: User,
        operation: Literal[1, -1],
        value: int,
        channel: str,
        app: OpenApp,
    ):
        value = abs(value)
        return cls.objects.create(
            order_id=order_id,
            user=user,
            value=value,
            operation=operation,
            channel=channel,
            app=app,
        )

    class Meta(TypedModelMeta):
        db_table = f"{DB_PREFIX}_user_credits_log"
        verbose_name = "用户积分记录"
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=["order_id", "app"], name="user_credits_log_order_app_unique"),
        ]


class WeiyiTreasureInfo(models.Model):
    commodity_uuid = models.CharField(max_length=150, unique=True, verbose_name="商品唯一标识")
    name = models.CharField(max_length=150, verbose_name="商品名")
    is_gold = models.BooleanField(default=False, verbose_name="是否是金卡")
    is_whitelist = models.BooleanField(default=False, verbose_name="是否是白名单")
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="价格")

    class Meta(TypedModelMeta):
        db_table = f"{DB_PREFIX}_weiyi_treasure_info"
        verbose_name = "唯艺藏品信息表"
        verbose_name_plural = verbose_name


class UserWeiyiTreasure(models.Model):
    class TypeMarketChoice(models.IntegerChoices):
        copyright = 1, "版权品"
        derivative = 2, "衍生品"
        digital_identity = 3, "数字身份"

    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    commodity_uuid = models.CharField(max_length=150, verbose_name="商品唯一标识")
    name = models.CharField(max_length=150, verbose_name="商品名")
    number = models.IntegerField(verbose_name="编号")
    cover = models.CharField(max_length=1024, verbose_name="图片")
    type_market = models.IntegerField(verbose_name="市场类型", choices=TypeMarketChoice.choices)
    # TODO 已经返利标记，无价格商品直接跳过
    # 金-银		0.5
    # 银-普		0.3
    # 金-银-普(间接)		0.1
    # 普-普		0.1


    class Meta(TypedModelMeta):
        db_table = f"{DB_PREFIX}_user_weiyi_treasure"
        verbose_name = "用户唯艺藏品表"
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=["commodity_uuid", "number"], name="weiyi_treasure_commodity_number_unique"),
        ]
        index_together = [["name", "number"]]

    @classmethod
    def update_or_create(
        cls,
        # unique
        commodity_uuid: str,
        number: int,
        # defaults
        user: User,
        name: str,
        cover: str,
        type_market: int,
    ):
        defaults = {
            "user": user,
            "name": name,
            "cover": cover,
            "type_market": type_market,
        }
        with transaction.atomic():
            obj, created = UserWeiyiTreasure.objects.select_for_update().get_or_create(
                commodity_uuid=commodity_uuid,
                number=number,
                defaults=defaults,
            )
            if created:
                return obj, created

            update_fields = []
            for k, v in defaults.items():
                if getattr(obj, k) != v:
                    setattr(obj, k, v)
                    update_fields.append(k)
            obj.save(update_fields=defaults)
            return obj, False
