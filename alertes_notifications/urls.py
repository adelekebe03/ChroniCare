from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet, AlertViewSet, MessageTemplateViewSet
from . import views

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification-api')
router.register(r'alerts',        AlertViewSet,        basename='alert-api')
router.register(r'templates',     MessageTemplateViewSet, basename='template-api')

urlpatterns = [
    # API DRF
    path('api/', include(router.urls)),

    # Dashboard principal
    path('',           views.monitoring_dashboard, name='alerts-dashboard'),
    path('monitoring/', views.monitoring_dashboard, name='monitoring-dashboard'),

    # Alertes médicales
    path('alerts/',                      views.alert_list,             name='alert-list'),
    path('alerts/<int:pk>/',             views.alert_detail,           name='alert-detail'),
    path('alerts/<int:pk>/resolve/',     views.alert_resolve_html,     name='alert-resolve'),
    path('alerts/<int:pk>/acknowledge/', views.alert_acknowledge_html, name='alert-acknowledge'),

    # Notifications utilisateur
    path('notifications/',                views.notification_list,          name='notification-list'),
    path('notifications/<int:pk>/',       views.notification_detail,        name='notification-detail'),
    path('notifications/mark-all-read/',  views.notification_mark_all_read, name='notification-mark-all-read'),

    # API badge (non-lue count pour la sidebar)
    path('api/notification-count/', views.notification_count_api, name='notification-count-api'),

    # Templates messages (admin only)
    path('templates/',                    views.template_page,   name='template-page'),
    path('templates/create/',            views.template_create, name='template-create'),
    path('templates/<int:pk>/delete/',   views.template_delete, name='template-delete'),
]
