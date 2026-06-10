from celery import shared_task

from django.utils import timezone

from datetime import datetime, timedelta

from .models import Appointment

from alertes_notifications.models import Notification


@shared_task
def envoyer_rappels():

    maintenant = timezone.now()

    dans_24h = maintenant + timedelta(hours=24)

    rdvs = Appointment.objects.filter(
        status='planifie',
        is_reminded=False,
    ).select_related(
        'patient',
        'doctor',
        'patient__compte_patient'
    )

    for rdv in rdvs:

        rdv_datetime = timezone.make_aware(
            datetime.combine(
                rdv.date,
                rdv.heure
            )
        )

        if maintenant < rdv_datetime <= dans_24h:

            telephone = rdv.patient.telephone

            message = (
                f"[ChroniCare] Rappel : RDV le "
                f"{rdv.date} à {rdv.heure} "
                f"avec Dr {rdv.doctor.get_full_name()}"
            )

            # Simulation SMS
            print(f"SMS → {telephone} : {message}")

            # Notification in-app
            if rdv.patient.compte_patient:

                Notification.objects.create(
                    user=rdv.patient.compte_patient,
                    appointment=rdv,
                    title="Rappel de rendez-vous",
                    message=message
                )

            rdv.is_reminded = True

            rdv.save(
                update_fields=['is_reminded']
            )