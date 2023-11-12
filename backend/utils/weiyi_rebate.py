from decimal import Decimal
from user.models import User, UserWeiyiTreasure, WeiyiTreasureInfo
from openapi.models import OpenApp
from django.db import transaction
from backend.utils.order_utils import get_order_id
from backend.settings import get_logger, get_redis_connection, REDIS_PREFIX

logger = get_logger()
redis_conn = get_redis_connection()

from redis.lock import Lock

app = OpenApp.objects.get(app_id="mall")

# TODO 积分倍率
CREDITS_PER_YUAN = 10000


@transaction.atomic()
def apply_user_buy_rebate(user: User, info: WeiyiTreasureInfo):
    if user.parent is None:
        return

    credits_total = info.price * CREDITS_PER_YUAN
    parent_value = 0
    if user.level == User.LevelChoice.B and user.parent_level == User.LevelChoice.A:
        parent_value = int(credits_total * Decimal("0.5"))
    elif user.level == User.LevelChoice.C and user.parent_level == User.LevelChoice.B:
        parent_value = int(credits_total * Decimal("0.3"))
    elif user.level == User.LevelChoice.C and user.parent_level == User.LevelChoice.C:
        parent_value = int(credits_total * Decimal("0.1"))

    if parent_value > 0:
        logger.info(
            f"name={info.name!r} user={user}:{user.level} parent={user.parent}:{user.parent_level} "
            f"value={parent_value} total={credits_total}"
        )
        user.parent.change_credits_and_log(
            order_id=get_order_id(),
            operation=1,
            value=parent_value,
            channel="返利",
            app=app,
        )

    if user.parent_parent is None:
        return

    if (
        user.level == User.LevelChoice.C
        and user.parent_level == User.LevelChoice.B
        and user.parent_parent_level == User.LevelChoice.A
    ):
        value = int(credits_total * Decimal("0.1"))
        logger.info(
            f"name={info.name!r} user={user}:{user.level} parent={user.parent}:{user.parent_level} "
            f"parent_parent={user.parent_parent}:{user.parent_parent_level}"
            f"value={value} total={credits_total}"
        )
        user.parent_parent.change_credits_and_log(
            order_id=get_order_id(),
            operation=1,
            value=value,
            channel="返利",
            app=app,
        )


def do_rebate():
    try:
        with Lock(
            redis=redis_conn,
            name=f"{REDIS_PREFIX}:lock:do_rebate",
            timeout=30,
            blocking=True,
            blocking_timeout=5,
        ):
            queryset = UserWeiyiTreasure.objects.filter(
                is_rebate=False,
                # 无价格商品直接排除
                commodity_uuid__in=WeiyiTreasureInfo.objects.values_list("commodity_uuid"),
            )
            for i in queryset:
                info = WeiyiTreasureInfo.objects.get(commodity_uuid=i.commodity_uuid)
                apply_user_buy_rebate(user=i.user, info=info)
    except Exception as e:
        logger.warning(e)
