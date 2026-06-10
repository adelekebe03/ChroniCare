"""
Services du module alertes & notifications — ChroniCare.

Conventions :
- create_alert()       → alerte médicale patient (visible équipe soignante)
- create_notification() → notification interne utilisateur (boîte de réception)
- Les fonctions métier chroniques envoient les deux (alerte + notifications équipe).
"""
from django.utils import timezone

from .models import Alert, Notification, MessageTemplate


# ────────────────────────────────────────────────────────────
# PRIMITIVES
# ────────────────────────────────────────────────────────────

def create_alert(
    patient,
    message,
    alert_type='warning',
    source='system',
    source_suivi=None,
    source_labtest=None,
):
    """Crée une alerte médicale liée à un patient."""
    return Alert.objects.create(
        patient=patient,
        message=message,
        alert_type=alert_type,
        source=source,
        source_suivi=source_suivi,
        source_labtest=source_labtest,
    )


def create_notification(user, title, message, level='info'):
    """Crée une notification interne pour un utilisateur du système."""
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        level=level,
    )


def mark_notification_as_read(notification):
    """Marque une notification comme lue."""
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    return notification


def mark_all_read(user):
    """Marque toutes les notifications d'un utilisateur comme lues."""
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)


def resolve_alert(alert, user=None):
    """Résout une alerte (appelle la méthode du modèle pour traçabilité)."""
    if user:
        alert.resolve(user)
    else:
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save(update_fields=['is_resolved', 'resolved_at'])
    return alert


def acknowledge_alert(alert, user):
    """Accusé de réception médecin : confirme avoir vu l'alerte."""
    alert.acknowledge(user)
    return alert


# ────────────────────────────────────────────────────────────
# TEMPLATES DE MESSAGES
# ────────────────────────────────────────────────────────────

def _render_template(code, context, fallback_title='Alerte médicale', fallback_message=None):
    """
    Cherche un MessageTemplate par code et rend le message avec le contexte.
    Retourne (title, message).
    """
    template = MessageTemplate.objects.filter(code=code).first()
    if not template:
        return fallback_title, fallback_message or context.get('message', '')
    return template.title, template.render(context)


# ────────────────────────────────────────────────────────────
# NOTIFICATION DE L'ÉQUIPE SOIGNANTE
# ────────────────────────────────────────────────────────────

def notifier_equipe_soignante(title, message, level='warning', exclude_user=None):
    """
    Notifie tous les médecins et infirmiers actifs du système.
    Dans un hôpital chronique, l'alerte est diffusée à l'équipe de garde
    car le patient peut ne pas avoir de médecin unique assigné.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    soignants = User.objects.filter(
        role__in=['doctor', 'nurse', 'admin'],
        is_active=True,
    )
    if exclude_user:
        soignants = soignants.exclude(pk=exclude_user.pk)

    notifications = [
        Notification(
            user=soignant,
            title=title,
            message=message,
            level=level,
        )
        for soignant in soignants
    ]
    Notification.objects.bulk_create(notifications)


# ────────────────────────────────────────────────────────────
# ALERTES MÉTIER — SUIVI MÉDICAL
# ────────────────────────────────────────────────────────────

def alerter_valeur_critique(patient, type_mesure, valeur, seuil, unite, suivi=None):
    """
    Génère une alerte critique + notifie l'équipe soignante
    quand une mesure dépasse le seuil critique (glycémie, tension, etc.).

    Exemple d'appel depuis suivi_medical/services.py :
        alerter_valeur_critique(patient, 'glycemie', 18.2, 16.0, 'mmol/L', suivi)
    """
    context = {
        'patient_nom': f"{patient.prenom} {patient.nom}",
        'valeur':      str(valeur),
        'seuil':       str(seuil),
        'unite':       unite,
        'type_mesure': type_mesure,
        'date':        timezone.now().strftime('%d/%m/%Y à %H:%M'),
    }

    template_code = f"{type_mesure}_critique"
    title, message = _render_template(
        template_code,
        context,
        fallback_title=f"Valeur critique — {type_mesure}",
        fallback_message=(
            f"{patient.prenom} {patient.nom} : {type_mesure} = {valeur} {unite} "
            f"(seuil critique : {seuil} {unite})."
        ),
    )

    alert = create_alert(
        patient=patient,
        message=message,
        alert_type='critical',
        source='suivi_medical',
        source_suivi=suivi,
    )

    notifier_equipe_soignante(title=title, message=message, level='urgent')

    return alert


def alerter_valeur_anormale(patient, type_mesure, valeur, seuil_min, seuil_max, unite, suivi=None):
    """
    Génère une alerte avertissement (non critique) + notifie le médecin du patient.
    """
    context = {
        'patient_nom': f"{patient.prenom} {patient.nom}",
        'valeur':      str(valeur),
        'seuil_min':   str(seuil_min),
        'seuil_max':   str(seuil_max),
        'unite':       unite,
        'type_mesure': type_mesure,
        'date':        timezone.now().strftime('%d/%m/%Y à %H:%M'),
    }

    template_code = f"{type_mesure}_anormal"
    title, message = _render_template(
        template_code,
        context,
        fallback_title=f"Valeur anormale — {type_mesure}",
        fallback_message=(
            f"{patient.prenom} {patient.nom} : {type_mesure} = {valeur} {unite} "
            f"(norme : {seuil_min}–{seuil_max} {unite})."
        ),
    )

    alert = create_alert(
        patient=patient,
        message=message,
        alert_type='warning',
        source='suivi_medical',
        source_suivi=suivi,
    )

    # Notifie les médecins uniquement pour un simple avertissement
    from django.contrib.auth import get_user_model
    User = get_user_model()
    for medecin in User.objects.filter(role='doctor', is_active=True):
        create_notification(medecin, title, message, level='warning')

    return alert


# ────────────────────────────────────────────────────────────
# ALERTES MÉTIER — LABORATOIRE
# ────────────────────────────────────────────────────────────

def alerter_resultat_labo_critique(patient, type_test, valeur, labtest=None):
    """
    Alerte critique quand un résultat de laboratoire est hors seuil critique.
    Appelée depuis laboratoire/services.py après validation du résultat.
    """
    message = (
        f"Résultat critique — {type_test} : {valeur}. "
        f"Patient : {patient.prenom} {patient.nom}. Intervention requise."
    )

    alert = create_alert(
        patient=patient,
        message=message,
        alert_type='critical',
        source='laboratoire',
        source_labtest=labtest,
    )

    notifier_equipe_soignante(
        title=f"Résultat labo critique — {type_test}",
        message=message,
        level='urgent',
    )

    return alert


def alerter_resultat_labo_anormal(patient, type_test, valeur, labtest=None):
    """Alerte avertissement pour résultat de labo anormal (non critique)."""
    message = (
        f"Résultat anormal — {type_test} : {valeur}. "
        f"Patient : {patient.prenom} {patient.nom}. Interprétation médicale recommandée."
    )

    alert = create_alert(
        patient=patient,
        message=message,
        alert_type='warning',
        source='laboratoire',
        source_labtest=labtest,
    )

    from django.contrib.auth import get_user_model
    User = get_user_model()
    for medecin in User.objects.filter(role='doctor', is_active=True):
        create_notification(medecin, f"Résultat labo anormal — {type_test}", message, level='warning')

    return alert


# ────────────────────────────────────────────────────────────
# ALERTES MÉTIER — PHARMACIE / TRAITEMENT CHRONIQUE
# ────────────────────────────────────────────────────────────

def alerter_renouvellement_imminent(patient, prescription, jours_restants):
    """
    Notifie le patient (via son compte) et le médecin que le renouvellement
    du traitement est imminent.
    """
    patient_user = getattr(patient, 'compte_patient', None)
    message = (
        f"Le traitement de {patient.prenom} {patient.nom} doit être renouvelé "
        f"dans {jours_restants} jour(s). Présentez-vous à la pharmacie."
    )

    if patient_user:
        create_notification(patient_user, "Renouvellement de traitement", message, level='warning')

    if prescription.medecin:
        create_notification(
            prescription.medecin,
            f"Renouvellement imminent — {patient.prenom} {patient.nom}",
            message,
            level='info',
        )

    return create_alert(
        patient=patient,
        message=message,
        alert_type='warning',
        source='renouvellement',
    )


def alerter_rupture_stock(patient, medication_nom, stock_restant):
    """Alerte rupture de stock pour un médicament d'un patient chronique."""
    message = (
        f"Rupture de stock — {medication_nom} ({stock_restant} unités restantes). "
        f"Réapprovisionnement requis pour {patient.prenom} {patient.nom}."
    )

    from django.contrib.auth import get_user_model
    User = get_user_model()
    for pharmacien in User.objects.filter(role='pharmacist', is_active=True):
        create_notification(pharmacien, f"Rupture — {medication_nom}", message, level='urgent')

    return create_alert(
        patient=patient,
        message=message,
        alert_type='critical',
        source='stock_pharmacie',
    )


# ────────────────────────────────────────────────────────────
# ESCALADE — ALERTES CRITIQUES NON ACCUSÉES
# ────────────────────────────────────────────────────────────

def escalader_alertes_non_accusees(heures=2):
    """
    À appeler périodiquement (tâche planifiée, ex: toutes les heures).

    Toute alerte critique non accusée depuis plus de `heures` heures
    déclenche une nouvelle notification urgente à toute l'équipe.
    """
    from datetime import timedelta
    seuil = timezone.now() - timedelta(hours=heures)

    alertes = Alert.objects.filter(
        alert_type='critical',
        is_resolved=False,
        acknowledged_by__isnull=True,
        created_at__lte=seuil,
    ).select_related('patient')

    for alert in alertes:
        notifier_equipe_soignante(
            title=f"ESCALADE — Alerte non accusée ({alert.patient})",
            message=(
                f"L'alerte critique créée le {alert.created_at:%d/%m/%Y à %H:%M} "
                f"pour {alert.patient.prenom} {alert.patient.nom} n'a pas été accusée. "
                f"Message : {alert.message}"
            ),
            level='urgent',
        )

    return alertes.count()
