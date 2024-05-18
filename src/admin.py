from django.contrib import admin

from .models import Project, Room, Message, MemberMessageSeen, RoomMember, \
    Task, Assignment


admin.site.site_title = "Site admin (DEV)"
admin.site.site_header = "Administration"
admin.site.index_title = "Site administration"


@admin.action(description="Activate selected projects")
def activate_projects(modeladmin, request, queryset):
    queryset.update(status='active')


@admin.action(description="Deactivate selected projects")
def deactivate_projects(modeladmin, request, queryset):
    queryset.update(status='on-hold')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "description", "title", "status"]
    list_select_related = ["manager_id", "created_by"]  # to avoid N + 1
    readonly_fields = ["id", "created_by"]
    list_filter = ["manager_id__title", "status", "title", "id", "created_by"]
    search_filter = ["manager_id__title", "status", "title", "id", "created_by"]
    actions = [activate_projects, deactivate_projects]


class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ["id", "room_id", "member_id", "latest_seen_message_id"]
    list_select_related = ["room_id", "member_id", "latest_seen_message_id"]
    readonly_fields = ["id"]
    list_filter = ["id", "room_id", "member_id"]
    search_filter = ["id", "room_id", "member_id"]


class RoomAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "type", "display_is_private", "owner"]
    list_select_related = ["owner"]
    readonly_fields = ["id"]
    list_filter = ["id", "title", "type"]
    search_filter = ["id", "title", "type"]

    def display_is_private(self, obj):
        return f"${obj.private}"

    display_is_private.short_description = "Is_private"
    display_is_private.admin_order_field = "Is_private"


class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "body", "is_seen", "sender_id", "room_id"]
    list_select_related = ["sender_id", "room_id"]
    readonly_fields = ["id"]
    list_filter = ["id", "sender_id", "room_id"]
    search_filter = ["id", "sender_id", "room_id"]


class MemberMessageSeenAdmin(admin.ModelAdmin):
    list_display = ["id", "message_id", "member_id"]
    list_select_related = ["message_id", "member_id"]
    readonly_fields = ["id"]
    list_filter = ["id", "message_id", "member_id"]
    search_filter = ["id", "message_id", "member_id"]


class TaskAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "title", "project_id", "public_room_id", "private_room_id",
                    "manager_id", "created_by"]
    list_select_related = ["project_id", "public_room_id", "private_room_id",
                           "manager_id", "created_by"]
    readonly_fields = ["id"]
    list_filter = ["id", "project_id", "manager_id"]
    search_filter = ["id", "project_id", "manager_id"]


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["id", "start_date", "end_date", "estimate_hours", "member_id",
                    "public_room_id", "private_room_id", "task_id", "created_by"]
    list_select_related = [
        "member_id",
        "public_room_id",
        "private_room_id",
        "task_id",
        "created_by",
    ]
    readonly_fields = ["id"]
    list_filter = ["id", "start_date", "end_date"]
    search_filter = ["id", "start_date", "end_date"]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(RoomMember, RoomMemberAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MemberMessageSeen, MemberMessageSeenAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Assignment, AssignmentAdmin)

