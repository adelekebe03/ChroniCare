from django.contrib import admin
from .models import AuditLog, SystemConfig
# Register your models here.

admin.site.register(AuditLog)
admin.site.register(SystemConfig)