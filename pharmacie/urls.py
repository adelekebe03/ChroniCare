from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MedicationViewSet, PrescriptionViewSet, MedicationLotViewSet, DispensationViewSet
from . import views

router = DefaultRouter()
router.register(r'medications',   MedicationViewSet,   basename='medication-api')
router.register(r'lots',          MedicationLotViewSet, basename='lot-api')
router.register(r'prescriptions', PrescriptionViewSet,  basename='prescription-api')
router.register(r'dispensations', DispensationViewSet,  basename='dispensation-api')

urlpatterns = [
    path('api/', include(router.urls)),

    # Dashboard
    path('', views.pharmacie_dashboard, name='pharmacie-dashboard'),

    # Prescriptions
    path('prescriptions/',                        views.prescription_list,         name='prescription-list'),
    path('prescriptions/<int:pk>/',               views.prescription_detail,       name='prescription-detail'),
    path('prescriptions/<int:pk>/edit/',          views.prescription_create_form,  name='prescription-create-form'),
    path('prescriptions/<int:pk>/delete/',        views.delete_prescription,       name='delete-prescription'),

    # Dispensation (POST = confirme, GET = page de confirmation)
    path('prescriptions/<int:prescription_id>/dispenser/', views.dispenser, name='dispenser'),

    # Médicaments et lots
    path('medications/',                views.medication_list,   name='medication-list'),
    path('medications/create/',         views.medication_create, name='medication-create'),
    path('lots/add/',                   views.add_lot,           name='add-lot'),
    path('lots/<int:pk>/delete/',       views.delete_lot,        name='delete-lot'),

    # Dispensations
    path('dispensations/',              views.dispensation_list,   name='dispensation-list'),
    path('dispensations/<int:pk>/',     views.dispensation_detail, name='dispensation-detail'),
    path('dispensations/<int:pk>/pdf/', views.dispensation_pdf,    name='dispensation-pdf'),
]
