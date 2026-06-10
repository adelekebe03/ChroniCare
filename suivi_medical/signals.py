from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SuiviMedical
from .services import check_alerts_suivi


@receiver(post_save, sender=SuiviMedical)
def trigger_alerts_suivi(sender, instance, created, **kwargs):

    if created:
        check_alerts_suivi(instance)