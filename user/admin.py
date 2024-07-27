from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Member


@admin.register(Member)
class AdminModel(admin.ModelAdmin):
    list_filter = ['title', 'email', 'id', 'is_admin']
    search_fields = ['title', 'email', 'phone', 'id']
    list_display = ['title', 'email', 'phone', 'is_admin']

