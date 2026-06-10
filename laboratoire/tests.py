
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LabTest
from .services import trigger_lab_alerts, compute_status, compute_is_abnormal
from django.utils import timezone


@receiver(post_save, sender=LabTest)
def analyse_lab_test(sender, instance, created, **kwargs):

    # 🔥 Cas création OU mise à jour
    if not instance:
        return

    # =========================
    # 1. recalcul automatique
    # =========================

    updated = False

    new_status = compute_status(instance)
    new_abnormal = compute_is_abnormal(instance)

    if instance.status != new_status:
        instance.status = new_status
        updated = True

    if instance.is_abnormal != new_abnormal:
        instance.is_abnormal = new_abnormal
        updated = True

    if updated:
        LabTest.objects.filter(id=instance.id).update(
            status=instance.status,
            is_abnormal=instance.is_abnormal
        )

    # =========================
    # 2. alertes seulement à la création
    # =========================

    if created:
        trigger_lab_alerts(instance)