from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet
from . import views

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')

urlpatterns = [
    # API
    path('api/', include(router.urls)),

    # HTML
    path('', views.patient_list, name='patient-list'),
    path('create/', views.patient_create, name='patient-create'),
    path('<int:pk>/', views.patient_detail, name='patient-detail'),
    path('<int:pk>/edit/', views.patient_update, name='patient-update'),
    path('<int:pk>/delete/', views.patient_delete, name='patient-delete'),
    path('<int:pk>/dossier/', views.dossier_medical, name='dossier-medical'),
]
