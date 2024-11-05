from django.contrib import admin

from .models import *

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'file')

