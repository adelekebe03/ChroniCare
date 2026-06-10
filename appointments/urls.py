from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet
from . import views

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment-api')

urlpatterns = [
    # API
    path('api/', include(router.urls)),

    # HTML
    path('', views.appointment_list, name='appointment-list'),
    path('create/', views.appointment_create, name='appointment-create'),
    path('calendar/', views.appointment_calendar, name='appointment-calendar'),
    path('mes-rendez-vous/', views.mes_rendez_vous, name='mes-rendez-vous'),
    path('mes-rdv-events/', views.patient_events, name='mes-rdv-events'),
    path('<int:pk>/', views.appointment_detail, name='appointment-detail'),
    path('<int:pk>/edit/', views.appointment_update, name='appointment-update'),
    path('<int:pk>/delete/', views.appointment_delete, name='appointment-delete'),
]
