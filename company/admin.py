from django.contrib import admin
from .models import *


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    pass


class AboutUsGalleryInline(admin.StackedInline):
    model = AboutUsGallery
    extra = 2

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    inlines = [AboutUsGalleryInline]



@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    pass

@admin.register(SocialMedia)
class SocialmediaAdmin(admin.ModelAdmin):
    pass