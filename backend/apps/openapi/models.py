from django.db import models
from typing import Literal
from backend.settings import DB_PREFIX
from backend.utils.typed_model_meta import TypedModelMeta


class OpenApp(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    name = models.CharField(max_length=150, verbose_name="应用名称")
    app_id = models.CharField(max_length=150, unique=True, verbose_name="应用ID")
    app_secret = models.CharField(max_length=150, verbose_name="应用密钥")

    class Meta(TypedModelMeta):
        db_table = f"{DB_PREFIX}_openapi_app"
        verbose_name = "开放应用表"
        verbose_name_plural = verbose_name
