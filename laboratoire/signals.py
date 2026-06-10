from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import LabTest
from .services import compute_is_abnormal, detect_maladie_from_labtest

User = get_user_model()


@receiver(pre_save, sender=LabTest)
def set_abnormal_flag(sender, instance, **kwargs):
    """Calcule is_abnormal automatiquement avant chaque sauvegarde."""
    instance.is_abnormal = compute_is_abnormal(instance)


@receiver(post_save, sender=LabTest)
def auto_link_maladie(sender, instance, created, **kwargs):
    """À la création, tente de lier automatiquement une maladie chronique."""
    if created:
        detect_maladie_from_labtest(instance)


@receiver(post_save, sender=LabTest)
def notify_lab_on_new_demande(sender, instance, created, **kwargs):
    """Notifie tous les utilisateurs du rôle lab quand une nouvelle analyse est prescrite."""
    if not created:
        return
    from alertes_notifications.services import create_notification
    lab_users = User.objects.filter(role='lab', is_active=True)
    message = (
        f"Nouvelle demande d'analyse : {instance.get_type_test_display()} "
        f"pour {instance.patient.nom} {instance.patient.prenom}"
        f"{' — URGENT' if instance.urgence else ''}."
    )
    for lab_user in lab_users:
        create_notification(
            lab_user,
            "Nouvelle analyse à réaliser",
            message,
            "urgent" if instance.urgence else "info",
        )
