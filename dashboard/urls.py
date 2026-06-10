from django.urls import path
from . import views

urlpatterns = [
    path('',           views.dashboard_page,      name='dashboard'),
    path('admin/',     views.admin_dashboard,      name='admin-dashboard'),
    path('medecin/',   views.medecin_dashboard,    name='medecin-dashboard'),
    path('infirmier/', views.infirmier_dashboard,  name='infirmier-dashboard'),
    path('patient/',   views.patient_dashboard,    name='patient-dashboard'),
    path('pharmacien/',views.pharmacien_dashboard, name='pharmacien-dashboard'),
    path('laboratoire/',views.laboratoire_dashboard,name='laboratoire-dashboard'),

    path('export/pdf/', views.export_dashboard_pdf, name='dashboard-export-pdf'),
    path('api/vitals/<int:patient_id>/', views.api_vitals_evolution, name='api-vitals-evolution'),
]
