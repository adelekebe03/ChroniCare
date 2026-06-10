from alertes_notifications.models import Notification
from suivi_medical.models import SuiviMedical


def send_appointment_reminder(appointment):

    if not appointment.is_reminded:

        Notification.objects.create(
            user=appointment.patient.compte_patient,
            appointment=appointment,
            title="Rappel RDV",
            message="Vous avez un rendez-vous bientôt"
        )

        appointment.is_reminded = True
        appointment.save()

def create_suivi_after_appointment(rdv):

    return SuiviMedical.objects.create(
        appointment=rdv,
        patient=rdv.patient,
        medecin=rdv.doctor,
        observations="Suivi généré après consultation"
    )


