from django.db import models, transaction
from django.db.models import F
from typing import Literal
from backend.settings import DB_PREFIX
from backend.utils.typed_model_meta import TypedModelMeta
from openapi.models import OpenApp


class User(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    phone = models.CharField(max_length=150, unique=True, verbose_name="手机号")
    credits = models.BigIntegerField(default=0, verbose_name="积分")

    express_name = models.CharField(max_length=150, default="", verbose_name="收货人")
    express_phone = models.CharField(max_length=150, default="", verbose_name="收货手机号码")
    express_area = models.CharField(max_length=150, default="", verbose_name="所在地区")
    express_address = models.CharField(max_length=150, default="", verbose_name="详细地址")

    def __str__(self):
        return self.phone

    @property
    def phone_mask(self):
        return self.phone[:3] + "****" + self.phone[-4:]

    @classmethod
    def get_or_create(cls, phone: str):
        user, _ = cls.objects.get_or_create(phone=phone)
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
            models.UniqueConstraint(fields=["order_id", "app"], name="order_id_app"),
        ]
