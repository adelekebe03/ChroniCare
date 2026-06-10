from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Patient
from alertes_notifications.services import create_notification


@receiver(post_save, sender=Patient)
def patient_created(sender, instance, created, **kwargs):

    if not created:
        return

    # notification admin ou créateur
    if instance.cree_par:

        create_notification(
            instance.cree_par,
            "Nouveau patient créé",
            f"Le patient {instance.nom} {instance.prenom} a été ajouté.",
            "info"
        )