from django.db.models import Sum
import typing
from user.models import User, UserWeiyiTreasure, WeiyiTreasureInfo, UserCreditsLog
from backend.settings import get_logger, get_redis_connection, REDIS_PREFIX

logger = get_logger()
redis_conn = get_redis_connection()

from redis.lock import Lock


def treasure_to_a():
    users = list(
        UserWeiyiTreasure.objects.filter(
            commodity_uuid__in=WeiyiTreasureInfo.objects.filter(
                is_gold=True,
            ).values_list("commodity_uuid")
        )
        .values_list("user", flat=True)
        .exclude(user__level=User.LevelChoice.A)
        .distinct()
    )

    if users:
        logger.info(users)
        User.objects.filter(id__in=users).update(level=User.LevelChoice.A)


def invie_c_to_b():
    users = list(
        User.objects.filter(
            level=User.LevelChoice.C,
            parent__level=User.LevelChoice.A,
        ).values_list("id", flat=True)
    )
    if users:
        logger.info(users)
        User.objects.filter(id__in=users).update(level=User.LevelChoice.B)


def credits_c_to_b():
    users = list(
        UserCreditsLog.objects.filter(user__in=User.objects.filter(level=User.LevelChoice.C), operation=1)
        .values("user")
        .annotate(credits_sum=Sum("value"))
        .filter(credits_sum__gte=100000)
        .values_list("user", flat=True)
    )
    if users:
        logger.info(users)
        User.objects.filter(id__in=users).update(level=User.LevelChoice.B)


def do_update_user_level():
    try:
        with Lock(
            redis=redis_conn,
            name=f"{REDIS_PREFIX}:lock:do_update_user_level",
            timeout=30,
            blocking=True,
            blocking_timeout=5,
        ):
            treasure_to_a()
            invie_c_to_b()
            credits_c_to_b()
    except Exception as e:
        logger.warning(e)
