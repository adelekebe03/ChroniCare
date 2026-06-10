from django.contrib import admin
from django.utils.html import format_html

from .models import Alert, Notification, MessageTemplate


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display  = [
        'patient', 'alert_type_badge', 'source', 'message_short',
        'is_acknowledged', 'is_resolved', 'created_at',
    ]
    list_filter   = ['alert_type', 'source', 'is_resolved']
    search_fields = ['patient__nom', 'patient__prenom', 'message']
    readonly_fields = [
        'created_at', 'acknowledged_by', 'acknowledged_at',
        'resolved_by', 'resolved_at',
    ]
    date_hierarchy = 'created_at'

    @admin.display(description='Sévérité')
    def alert_type_badge(self, obj):
        colors = {'critical': '#791F1F', 'warning': '#633806', 'info': '#0C447C'}
        bg = {'critical': '#FCEBEB', 'warning': '#FAEEDA', 'info': '#E6F1FB'}
        c = colors.get(obj.alert_type, '#000')
        b = bg.get(obj.alert_type, '#eee')
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;">{}</span>',
            b, c, obj.get_alert_type_display(),
        )

    @admin.display(description='Message')
    def message_short(self, obj):
        return obj.message[:80] + '…' if len(obj.message) > 80 else obj.message

    @admin.display(boolean=True, description='Accusée')
    def is_acknowledged(self, obj):
        return obj.acknowledged_by is not None


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['user', 'title', 'level', 'is_read', 'created_at']
    list_filter   = ['level', 'is_read']
    search_fields = ['user__username', 'user__first_name', 'title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display  = ['title', 'code', 'type', 'updated_at']
    list_filter   = ['type']
    search_fields = ['title', 'code', 'content']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'code': ('title',)}
