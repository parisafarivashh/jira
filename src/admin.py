from django.contrib import admin

from .models import Project, Room, Message, MemberMessageSeen, RoomMember

admin.site.register(Project)
admin.site.register(Room)
admin.site.register(RoomMember)
admin.site.register(Message)
admin.site.register(MemberMessageSeen)

