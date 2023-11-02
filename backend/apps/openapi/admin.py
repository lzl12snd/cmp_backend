from django.contrib import admin
from openapi.models import OpenApp


@admin.register(OpenApp)
class OpenAppAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
