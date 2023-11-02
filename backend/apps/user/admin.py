from django.contrib import admin
from user.models import User, UserCreditsLog


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "phone", "credits")


@admin.register(UserCreditsLog)
class UserCreditsLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "operation", "value")
