"""
URL configuration for ChroniCare project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),

    # FRONTEND HTML
    path('', include('core.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('patients/', include('patients.urls')),
    path('appointments/', include('appointments.urls')),
    path('pharmacie/', include('pharmacie.urls')),
    path('laboratoire/', include('laboratoire.urls')),
    path('maladies/', include('maladies.urls')),
    path('suivi-medical/', include('suivi_medical.urls')),
    path('users/', include('users.urls')),
    path('alertes/', include('alertes_notifications.urls')),

    # AUTH JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
