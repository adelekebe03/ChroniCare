"""
Tâches Celery planifiées — Alertes & Notifications ChroniCare.

Planification dans ChroniCare/celery.py :
  - verifier_renouvellements   : chaque jour à 8h00
  - escalader_alertes_critiques : toutes les 2 heures
  - notifier_stock_critique    : chaque jour à 7h00
"""
from celery import shared_task
from django.utils import timezone


# ── 1. Renouvellements de traitement imminents ───────────────────────────────

@shared_task(name='alertes_notifications.verifier_renouvellements')
def verifier_renouvellements():
    """
    Vérifie chaque jour les prescriptions dont le renouvellement
    est dans les 7 prochains jours et notifie le patient + le médecin.
    """
    from datetime import timedelta
    from pharmacie.models import Prescription
    from alertes_notifications.services import alerter_renouvellement_imminent

    aujourd_hui = timezone.now().date()
    dans_7_jours = aujourd_hui + timedelta(days=7)

    prescriptions = (
        Prescription.objects
        .filter(
            statut__in=['en_attente', 'active'],
            date_prochain_renouvellement__lte=dans_7_jours,
            date_prochain_renouvellement__gte=aujourd_hui,
        )
        .select_related('patient', 'medecin', 'patient__compte_patient')
    )

    count = 0
    for prescription in prescriptions:
        jours = (prescription.date_prochain_renouvellement - aujourd_hui).days
        alerter_renouvellement_imminent(
            patient=prescription.patient,
            prescription=prescription,
            jours_restants=jours,
        )

        # Email au patient
        patient_user = getattr(prescription.patient, 'compte_patient', None)
        if patient_user and patient_user.email:
            _envoyer_email_renouvellement(patient_user, prescription, jours)

        count += 1

    return f"{count} alerte(s) de renouvellement envoyée(s)."


def _envoyer_email_renouvellement(user, prescription, jours_restants):
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            subject="[ChroniCare] Renouvellement de traitement à prévoir",
            message=(
                f"Bonjour {user.get_full_name() or user.username},\n\n"
                f"Votre traitement doit être renouvelé dans {jours_restants} jour(s) "
                f"(le {prescription.date_prochain_renouvellement:%d/%m/%Y}).\n\n"
                f"Présentez-vous à la pharmacie de votre établissement "
                f"avec votre ordonnance.\n\n"
                f"— L'équipe ChroniCare"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        pass


# ── 2. Escalade des alertes critiques non accusées ───────────────────────────

@shared_task(name='alertes_notifications.escalader_alertes_critiques')
def escalader_alertes_critiques():
    """
    Toutes les 2 heures : re-notifie l'équipe soignante pour toute
    alerte critique qui n'a pas encore été accusée de réception.
    """
    from alertes_notifications.services import escalader_alertes_non_accusees

    nb = escalader_alertes_non_accusees(heures=2)
    return f"{nb} alerte(s) critique(s) escaladée(s)."


# ── 3. Stock médicaments critique ────────────────────────────────────────────

@shared_task(name='alertes_notifications.notifier_stock_critique')
def notifier_stock_critique():
    """
    Chaque jour à 7h00 : détecte les médicaments en rupture de stock
    et notifie tous les pharmaciens actifs.
    """
    from pharmacie.models import Medication
    from users.models import User
    from alertes_notifications.services import create_notification

    meds_en_rupture = [
        m for m in Medication.objects.prefetch_related('lots').all()
        if m.est_en_rupture
    ]

    if not meds_en_rupture:
        return "Aucun médicament en rupture de stock."

    pharmaciens = list(User.objects.filter(role='pharmacist', is_active=True))
    if not pharmaciens:
        return f"{len(meds_en_rupture)} rupture(s) détectée(s) — aucun pharmacien actif à notifier."

    for med in meds_en_rupture:
        message = (
            f"Stock critique — {med.nom} : {med.stock_total} unité(s) restante(s) "
            f"(seuil minimum : {med.stock_minimum}). Réapprovisionnement requis."
        )
        for pharmacien in pharmaciens:
            create_notification(
                user=pharmacien,
                title=f"Rupture stock — {med.nom}",
                message=message,
                level='urgent',
            )

    return (
        f"{len(meds_en_rupture)} rupture(s) détectée(s), "
        f"{len(pharmaciens)} pharmacien(s) notifié(s)."
    )


# ── 4. Rappels de rendez-vous (migré depuis appointments/tasks.py) ───────────

@shared_task(name='alertes_notifications.envoyer_rappels_rdv')
def envoyer_rappels_rdv():
    """
    Chaque heure : envoie un rappel in-app aux patients dont le RDV
    est dans les 24 prochaines heures et qui n'ont pas encore été rappelés.
    """
    from datetime import datetime, timedelta
    from appointments.models import Appointment
    from alertes_notifications.services import create_notification

    maintenant = timezone.now()
    dans_24h = maintenant + timedelta(hours=24)

    rdvs = (
        Appointment.objects
        .filter(status='planifie', is_reminded=False)
        .select_related('patient', 'doctor', 'patient__compte_patient')
    )

    count = 0
    for rdv in rdvs:
        rdv_datetime = timezone.make_aware(
            datetime.combine(rdv.date, rdv.heure)
        )

        if maintenant < rdv_datetime <= dans_24h:
            message = (
                f"Rappel : vous avez un rendez-vous le {rdv.date:%d/%m/%Y} "
                f"à {rdv.heure:%H:%M} avec Dr {rdv.doctor.get_full_name()}."
            )
            patient_user = rdv.patient.compte_patient

            # Notification in-app
            if patient_user:
                create_notification(
                    user=patient_user,
                    title="Rappel de rendez-vous",
                    message=message,
                    level='info',
                )

                # Email au patient (si adresse disponible)
                _envoyer_email_rappel(patient_user, rdv, message)

            rdv.is_reminded = True
            rdv.save(update_fields=['is_reminded'])
            count += 1

    return f"{count} rappel(s) envoyé(s)."


def _envoyer_email_rappel(user, rdv, message):
    """Envoie un email de rappel au patient si son adresse est renseignée."""
    if not user.email:
        return
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            subject="[ChroniCare] Rappel de rendez-vous",
            message=(
                f"Bonjour {user.get_full_name() or user.username},\n\n"
                f"{message}\n\n"
                f"Motif : {rdv.motif or 'Consultation générale'}\n\n"
                f"En cas d'empêchement, contactez votre médecin.\n\n"
                f"— L'équipe ChroniCare"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        pass
