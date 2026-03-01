from django.contrib import admin

from .models import Order, Key, OrderKeyTg

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'token_preview', 'created_at')
    search_fields = ('key', 'token')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def token_preview(self, obj):
        """Показывать только первые 50 символов токена"""
        if len(obj.token) > 50:
            return obj.token[:50] + '...'
        return obj.token
    token_preview.short_description = 'Access Token'

@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'tariff', 'is_used')
    list_filter = ('tariff', 'is_used')
    search_fields = ('key',)

@admin.register(OrderKeyTg)
class OrderKeyTgAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'tg_id', 'created_at')
    search_fields = ('key', 'tg_id')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

