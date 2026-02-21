from django.contrib import admin

from .models import Order

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
