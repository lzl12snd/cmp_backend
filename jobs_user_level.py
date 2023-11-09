from __future__ import annotations

import os
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django

django.setup()

from user.models import User, UserWeiyiTreasure, WeiyiTreasureInfo


def bc_to_a():
    new_gold_users = list(
        UserWeiyiTreasure.objects.filter(
            commodity_uuid__in=WeiyiTreasureInfo.objects.filter(
                is_gold=True,
            ).values_list("commodity_uuid")
        )
        .values_list("user", flat=True)
        .exclude(user__level=User.LevelChoice.A)
        .distinct()
    )

    User.objects.filter(id__in=new_gold_users).update(level=User.LevelChoice.A)


def bc_to_cb():
    users = User.objects.exclude(level=User.LevelChoice.A)
    for user in users:
        if user.level == User.LevelChoice.B and user.parent is None:
            user.level = User.LevelChoice.C
            user.save(update_fields=["level"])
            continue

        if user.level == User.LevelChoice.C and user.parent and user.parent.level == User.LevelChoice.A:
            user.level = User.LevelChoice.B
            user.save(update_fields=["level"])
            continue
