from django.contrib import admin
from .models import MyUser


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

