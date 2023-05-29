from django.contrib import admin
from .models import MyUser, Follow


@admin.register(MyUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
    )
    list_editable = ('role',)
    search_fields = ('username',)
    list_filter = ('role',)
    empty_value_display = '-пусто-'

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author',
    )
    list_editable = ('author',)
    empty_value_display = '-пусто-'
