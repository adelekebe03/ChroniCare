from django.shortcuts import render, redirect
from rest_framework import viewsets

from .models import SystemConfig, AuditLog
from .serializers import SystemConfigSerializer, AuditLogSerializer
from users.permissions import IsAdmin


class SystemConfigViewSet(viewsets.ModelViewSet):
    """Configuration de l'établissement — admin uniquement."""
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAdmin]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Journal d'audit — lecture seule, admin uniquement.
    ReadOnlyModelViewSet n'expose que list et retrieve (jamais de modification).
    """
    queryset = AuditLog.objects.all().order_by('-date_action')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]


def home(request):
    """
    Page d'accueil publique.
    Utilisateur connecté  → redirigé vers son dashboard de rôle.
    Utilisateur anonyme   → page de présentation avec les données SystemConfig.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    config = SystemConfig.objects.first()
    return render(request, 'core/home.html', {'config': config})
