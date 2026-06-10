from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Appointment
from alertes_notifications.models import Notification


@receiver(post_save, sender=Appointment)
def create_appointment_notification(sender, instance, created, **kwargs):

    if created:

        # 🔔 Notification patient
        if instance.patient and instance.patient.compte_patient:
            Notification.objects.create(
                user=instance.patient.compte_patient,
                appointment=instance,
                title="Nouveau rendez-vous",
                message=f"RDV le {instance.date} à {instance.heure}"
            )

        # 🔔 Notification médecin
        if instance.doctor:
            Notification.objects.create(
                user=instance.doctor,
                appointment=instance,
                title="Nouveau rendez-vous patient",
                message=f"RDV avec {instance.patient}"
            )