from django.contrib import admin

from .models import Following, User


class UserAdmin(admin.ModelAdmin):
    """Админка для пользователей."""

    list_display = ('id', 'email', 'username', 'first_name', 'last_name',)
    list_filter = ('email', 'username')


class FollowingAdmin(admin.ModelAdmin):
    """Админка для подписки."""

    list_display = ('user', 'following')


admin.site.register(User, UserAdmin)
admin.site.register(Following, FollowingAdmin)
