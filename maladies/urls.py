from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (MaladieViewSet,PatientMaladieViewSet,SeuilAlerteViewSet )
from . import views


router = DefaultRouter()

router.register(r'Maladie', MaladieViewSet)
router.register(r'patient-maladies', PatientMaladieViewSet)
router.register(r'seuils', SeuilAlerteViewSet)

urlpatterns = [
     path('api/', include((router.urls))),

    # FRONTEND HTML
    path('list/', views.maladie_list, name='maladie-list'),
    path('create/', views.maladie_create, name='maladie-create'),
    path('<int:pk>/', views.maladie_detail, name='maladie-detail'),
    path('<int:pk>/update/', views.maladie_update, name='maladie-update'),
    path('<int:pk>/delete/', views.maladie_delete, name='maladie-delete'),
    path('patient-maladie/', views.patient_maladie_list, name='patient-maladie-list'),
    path('patient-maladie/create/', views.patient_maladie_create, name='patient-maladie-create'),
    path('patient-maladie/<int:pk>/update/', views.patient_maladie_update, name='patient-maladie-update'),
    path('patient-maladie/<int:pk>/delete/', views.patient_maladie_delete, name='patient-maladie-delete'),
]