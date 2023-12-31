"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import datetime
import logging
from functools import partial
from typing import Type, TypeAlias, Union
from urllib.parse import urljoin

from django.contrib import admin
from django.core.paginator import InvalidPage
from django.db.models.fields.files import FieldFile
from django.http import HttpRequest, HttpResponse
from django.urls import include, path
from ninja import NinjaAPI
from ninja.errors import AuthenticationError, ValidationError
from ninja.renderers import JSONRenderer
from ninja.responses import NinjaJSONEncoder

from backend.settings import USE_TZ

logger = logging.getLogger("django")


class CustomJsonEncoder(NinjaJSONEncoder):
    def default(self, o):
        if isinstance(o, FieldFile):
            return urljoin(o.storage.base_url, o.name)
        if not USE_TZ and isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            return o.strftime("%Y/%m/%d")
        try:
            return super().default(o)
        except TypeError:
            logger.error((f"Object of type {o.__class__.__name__} {repr(o)} is not JSON serializable"))
            return repr(o)


class CustomJSONRenderer(JSONRenderer):
    encoder_class = CustomJsonEncoder


api = NinjaAPI(
    title="Open API",
    version="1.0.0",
    renderer=CustomJSONRenderer(),
)
api_back = NinjaAPI(
    title="Open API back",
    version="back 1.0.0",
    renderer=CustomJSONRenderer(),
)
api_open = NinjaAPI(
    title="Open API open",
    version="open 1.0.0",
    description="""
所有接口均以 HTTP Basic Auth 登录验证. 测试 app_id: `test`, app_secret: `test`, 所以请求头应该是 `Authorization: Basic dGVzdDp0ZXN0`


<details>
  <summary>响应示例</summary>

需要先判断 status_code == 200 确保请求成功, 再进行判断 code == 200 操作成功

正常响应
```
{
  "code": 200,
  "msg": "OK",
  "data": {
    "pong": "test"
  }
}
```

请求成功但操作错误响应
```
{
  "code": -1,
  "msg": "..."
}
```

翻页正常响应
```
{
    "code": 200,
    "msg": "OK",
    "data": [], // 数据列表
    "total": 0, // 记录总数
    "total_page": 1 // 总页数
}
```

</details>

""",
    renderer=CustomJSONRenderer(),
)


def set_exception_handlers(api: NinjaAPI):
    @api.exception_handler(AuthenticationError)
    def authentication_error_handler(request: HttpRequest, exc: AuthenticationError) -> HttpResponse:
        return api.create_response(
            request,
            {"code": 401, "msg": "登录失效"},
            status=401,
        )

    @api.exception_handler(ValidationError)
    def validation_error_handler(request: HttpRequest, exc: ValidationError) -> HttpResponse:
        logger.warning(exc.errors)
        if request.method == "POST":
            try:
                logger.warning(request.body)
            except Exception:
                pass
        return api.create_response(
            request,
            {"code": 422, "msg": "参数错误", "data": exc.errors},
            status=422,
        )

    @api.exception_handler(InvalidPage)
    def invalid_page_handler(request: HttpRequest, exc: InvalidPage) -> HttpResponse:
        return api.create_response(
            request,
            {"code": 400, "msg": f"页码错误: {exc}"},
            status=400,
        )

    @api.exception_handler(ValueError)
    def value_error_handler(request: HttpRequest, exc: ValueError) -> HttpResponse:
        logger.info(exc)
        return api.create_response(
            request,
            {"code": -1, "msg": f"{exc}"},
            status=200,
        )

    @api.exception_handler(Exception)
    def exception_handler(request: HttpRequest, exc: Exception) -> HttpResponse:
        logger.exception(exc)
        return api.create_response(
            request,
            {"code": 500, "msg": f"内部错误: {exc}"},
            status=500,
        )

    return (
        authentication_error_handler,
        validation_error_handler,
        invalid_page_handler,
        value_error_handler,
        exception_handler,
    )


set_exception_handlers(api)
set_exception_handlers(api_back)
set_exception_handlers(api_open)

from user.api import router as user_router
from goods.api import router as goods_router
from order.api import router as order_router

api.add_router("/", user_router)
api.add_router("/", goods_router)
api.add_router("/", order_router)

from back.api_back import router as back_back_router

api_back.add_router("/", back_back_router)

from openapi.api import router as openapi_router

api_open.add_router("/", openapi_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("api/open/", api_open.urls),
    path("api/back/", api_back.urls),
]
