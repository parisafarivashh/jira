from django.contrib import admin

from .models import Project, Room, Message

admin.site.register(Project)
admin.site.register(Room)
admin.site.register(Message)

