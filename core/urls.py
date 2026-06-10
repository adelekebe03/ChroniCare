from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SystemConfigViewSet, AuditLogViewSet, home

router = DefaultRouter()
router.register(r'config',    SystemConfigViewSet, basename='config')
router.register(r'audit-log', AuditLogViewSet,     basename='audit-log')

urlpatterns = [
    path('api/', include(router.urls)),
    path('',     home, name='home'),
]
