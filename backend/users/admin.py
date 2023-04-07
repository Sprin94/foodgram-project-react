from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ модель User."""


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ модель Follow."""
