from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PatientMaladie
from .services import get_patient_maladie_summary
from maladies.services import detect_maladie_from_labtest


# =========================
# POST SAVE PATIENT MALADIE
# =========================
@receiver(post_save, sender=PatientMaladie)
def patient_maladie_post_save(sender, instance, created, **kwargs):

    # ici tu peux ajouter notifications futures
    summary = get_patient_maladie_summary(instance.patient)

    # DEBUG (optionnel)
    print("Résumé patient :", summary)
  
