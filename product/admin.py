from django.contrib import admin

from .models import *
class ProductAttributeInline(admin.StackedInline):
    model = ProductAttribute
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductAttributeInline]
    list_display = ('title', 'desc', 'size','price')

@admin.register(WebOrder)
class WebOrderaAdmin(admin.ModelAdmin):
    pass


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    pass