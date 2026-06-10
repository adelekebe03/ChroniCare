from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabTestViewSet
from . import views

router = DefaultRouter()
router.register(r'analyses', LabTestViewSet, basename='analyse')

urlpatterns = [
    path('api/', include(router.urls)),

    # Liste et détail
    path('',          views.labtest_list,   name='labtest-list'),
    path('<int:pk>/', views.labtest_detail, name='labtest-detail'),

    # Flux médecin — création depuis un suivi médical
    path('from-suivi/<int:suivi_pk>/', views.labtest_create_from_suivi, name='labtest-create-from-suivi'),

    # Flux lab — saisie et validation
    path('<int:pk>/result/',   views.labtest_result,   name='labtest-result'),
    path('<int:pk>/validate/', views.labtest_validate, name='labtest-validate'),

    # Flux médecin — interprétation
    path('<int:pk>/interpret/', views.labtest_mark_interpreted, name='labtest-interpret'),
]
