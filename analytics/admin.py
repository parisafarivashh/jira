from django.contrib import admin

from .models import ObjectViewed


@admin.register(ObjectViewed)
class ObjectViewAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'object_id', 'content_object', 'time']

    list_select_related = ['content_type', 'user']
    readonly_fields = ['object_id', 'content_object', 'content_type']
    list_filter = ['user', 'time']
    list_search = ['user']
    actions = ['update']

    @admin.action(description='Updated selected ip')
    def update(self, request, queryset):
        queryset.update(ip_address='localhost')

