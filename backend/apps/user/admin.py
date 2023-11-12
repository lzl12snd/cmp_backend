from django.contrib import admin
from user.models import User, UserCreditsLog, WeiyiTreasureInfo


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "phone", "credits")
    raw_id_fields = ("parent",)

@admin.register(UserCreditsLog)
class UserCreditsLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "operation", "value")


@admin.register(WeiyiTreasureInfo)
class WeiyiTreasureInfoAdmin(admin.ModelAdmin):
    list_display = ("commodity_uuid", "name", "is_gold", "is_whitelist", "price")
