from django.utils import timezone
from alertes_notifications.services import create_alert, create_notification
from alertes_notifications.models import Alert
from maladies.models import Maladie
from .models import LabTest

# ── Seuils de référence par type d'analyse ───────────────────────────────────
# critique_min / critique_max : valeurs au-delà desquelles le statut = critique
TYPE_TEST_DEFAULTS = {
    'glycemie': {
        'seuil_min':   0.70, 'seuil_max':   1.10, 'unite': 'g/L',
        'critique_min': 0.50, 'critique_max': 2.00,
    },
    'cd4': {
        'seuil_min':   500,  'seuil_max':   None, 'unite': 'cells/mm³',
        'critique_min': 100, 'critique_max': None,
    },
    'charge_virale': {
        'seuil_min':   None, 'seuil_max':   40,      'unite': 'copies/mL',
        'critique_min': None, 'critique_max': 100_000,
    },
    'nfs': {
        'seuil_min': None, 'seuil_max': None, 'unite': '',
        'critique_min': None, 'critique_max': None,
    },
    'creatinine': {
        'seuil_min':   6.0,  'seuil_max':  12.0,  'unite': 'mg/L',
        'critique_min': None, 'critique_max': 20.0,
    },
    'uree': {
        'seuil_min':   0.15, 'seuil_max':  0.45,  'unite': 'g/L',
        'critique_min': None, 'critique_max': 0.70,
    },
    'transaminases': {
        'seuil_min':   None, 'seuil_max':  40.0,  'unite': 'UI/L',
        'critique_min': None, 'critique_max': 200.0,
    },
    'hemoglobine': {
        'seuil_min':   12.0, 'seuil_max':  18.0,  'unite': 'g/dL',
        'critique_min': 7.0, 'critique_max': 20.0,
    },
    'cholesterol': {
        'seuil_min':   None, 'seuil_max':   2.0,  'unite': 'g/L',
        'critique_min': None, 'critique_max': 3.0,
    },
    'tension': {
        'seuil_min':   None, 'seuil_max':  14.0,  'unite': 'cmHg',
        'critique_min': None, 'critique_max': 18.0,
    },
    'autre': {
        'seuil_min': None, 'seuil_max': None, 'unite': '',
        'critique_min': None, 'critique_max': None,
    },
}

# ── Mapping type d'analyse → champ(s) de SuiviMedical ────────────────────────
# Valeur simple : str (nom du champ)
# Tension : tuple (champ_systolique, champ_diastolique)
FIELD_MAP = {
    'glycemie':      'glycemie',
    'cd4':           'cd4',
    'charge_virale': 'charge_virale',
    'creatinine':    'creatinine',
    'uree':          'uree',
    'transaminases': 'transaminases',
    'hemoglobine':   'hemoglobine',
    'cholesterol':   'cholesterol',
    'tension':       ('tension_systolique', 'tension_diastolique'),
}

# Mots-clés pour auto-lier la maladie chronique
MALADIE_KEYWORDS = {
    'glycemie':      'diab',
    'cd4':           'vih',
    'charge_virale': 'vih',
    'tension':       'hyper',
    'cholesterol':   'card',
    'creatinine':    'rein',
    'uree':          'rein',
}


# ── 1. Détection anomalie ─────────────────────────────────────────────────────

def compute_is_abnormal(lab_test):
    if lab_test.status in ('anormal', 'critique'):
        return True
    if lab_test.valeur is not None:
        if lab_test.seuil_min is not None and lab_test.valeur < lab_test.seuil_min:
            return True
        if lab_test.seuil_max is not None and lab_test.valeur > lab_test.seuil_max:
            return True
    return False


# ── 2. Calcul du statut avec seuil critique ───────────────────────────────────

def compute_status(lab_test):
    """Retourne en_attente / normal / anormal / critique selon valeur et seuils."""
    if lab_test.valeur is None:
        return 'en_attente'

    v = lab_test.valeur
    defaults = TYPE_TEST_DEFAULTS.get(lab_test.type_test, {})
    crit_min = defaults.get('critique_min')
    crit_max = defaults.get('critique_max')

    # Vérification critique en premier
    if crit_min is not None and v < crit_min:
        return 'critique'
    if crit_max is not None and v > crit_max:
        return 'critique'

    s_min = lab_test.seuil_min
    s_max = lab_test.seuil_max
    if s_min is not None and v < s_min:
        return 'anormal'
    if s_max is not None and v > s_max:
        return 'anormal'
    return 'normal'


# ── 3. Alertes médicales ──────────────────────────────────────────────────────

def trigger_lab_alerts(lab_test):
    patient   = lab_test.patient
    user      = getattr(patient, 'compte_patient', None)
    type_test = lab_test.type_test
    v         = lab_test.valeur

    def _alerte(message, alert_type, source, notif_title, notif_msg, notif_type):
        if not Alert.objects.filter(patient=patient, message=message, is_resolved=False).exists():
            create_alert(patient, message, alert_type=alert_type, source=source)
            if user:
                create_notification(user, notif_title, notif_msg, notif_type)

    if type_test == 'glycemie' and v:
        if v > 2.0:
            _alerte("Glycémie critique", "critical", "lab_glycemia",
                    "Alerte critique glycémie", "Votre glycémie est à un niveau critique.", "urgent")
        elif v > 1.26:
            _alerte("Glycémie élevée", "warning", "lab_glycemia",
                    "Alerte glycémie", "Votre glycémie est élevée.", "urgent")

    if type_test == 'cd4' and v:
        if v < 100:
            _alerte("Immunité critique (CD4 < 100)", "critical", "lab_cd4",
                    "Alerte critique CD4", "Votre taux de CD4 est à un niveau critique.", "urgent")
        elif v < 200:
            _alerte("Immunité très basse (CD4)", "critical", "lab_cd4",
                    "Alerte immunitaire", "Votre taux de CD4 est bas.", "urgent")

    if type_test == 'tension' and v:
        if v > 18:
            _alerte("Hypertension critique", "critical", "lab_bp",
                    "Alerte critique tension", "Votre tension est à un niveau critique.", "urgent")
        elif v > 14:
            _alerte("Hypertension", "warning", "lab_bp",
                    "Alerte tension", "Votre tension est élevée.", "warning")

    if type_test == 'charge_virale' and v:
        if v > 100_000:
            _alerte("Charge virale critique", "critical", "lab_viral_load",
                    "Alerte critique charge virale", "Votre charge virale est à un niveau critique.", "urgent")
        elif v > 1000:
            _alerte("Charge virale élevée", "warning", "lab_viral_load",
                    "Alerte charge virale", "Votre charge virale est élevée.", "urgent")

    if type_test == 'hemoglobine' and v:
        if v < 7.0:
            _alerte("Anémie sévère (hémoglobine critique)", "critical", "lab_hemo",
                    "Alerte critique hémoglobine", "Votre hémoglobine est à un niveau critique.", "urgent")
        elif v < 12.0:
            _alerte("Anémie détectée", "warning", "lab_hemo",
                    "Alerte hémoglobine", "Votre taux d'hémoglobine est bas.", "warning")

    if type_test == 'creatinine' and v and v > 12.0:
        _alerte("Créatinine élevée", "warning", "lab_creatinine",
                "Alerte rénale", "Votre créatinine est élevée.", "warning")

    if type_test == 'cholesterol' and v and v > 2.0:
        _alerte("Cholestérol élevé", "warning", "lab_cholesterol",
                "Alerte cholestérol", "Votre cholestérol est élevé.", "warning")

    if type_test == 'transaminases' and v and v > 40:
        _alerte("Transaminases élevées", "warning", "lab_transaminases",
                "Alerte hépatique", "Vos transaminases sont élevées.", "warning")


# ── 4. Mise à jour structurée du suivi médical ───────────────────────────────

def update_suivi_from_labtest(labtest):
    """Propage les valeurs de l'analyse vers le suivi médical + trace la source."""
    suivi = labtest.suivi
    if not suivi or labtest.valeur is None:
        return None

    mapping = FIELD_MAP.get(labtest.type_test)
    if not mapping:
        return suivi

    sources = suivi.sources_biologiques or {}

    if isinstance(mapping, tuple):
        # Tension : systolique + diastolique
        champ_sys, champ_dia = mapping
        setattr(suivi, champ_sys, int(labtest.valeur))
        sources[champ_sys] = 'analyse_labo'
        if labtest.valeur_secondaire is not None:
            setattr(suivi, champ_dia, int(labtest.valeur_secondaire))
            sources[champ_dia] = 'analyse_labo'
    else:
        setattr(suivi, mapping, labtest.valeur)
        sources[mapping] = 'analyse_labo'

    suivi.sources_biologiques = sources
    suivi.save()
    return suivi


# ── 5. Détection automatique de la maladie liée ──────────────────────────────

def detect_maladie_from_labtest(labtest):
    keyword = MALADIE_KEYWORDS.get(labtest.type_test)
    if keyword:
        maladie = Maladie.objects.filter(nom__icontains=keyword).first()
        if maladie:
            labtest.maladie = maladie
            labtest.save(update_fields=['maladie'])
    return labtest


# ── 6. Notification au médecin prescripteur ──────────────────────────────────

def notify_prescripteur_result_ready(labtest):
    prescripteur = labtest.prescripteur
    if not prescripteur:
        return
    statut_label = labtest.get_status_display()
    niveau = 'urgent' if labtest.status in ('anormal', 'critique') else 'info'
    create_notification(
        prescripteur,
        f"Résultat disponible : {labtest.get_type_test_display()}",
        (
            f"L'analyse {labtest.get_type_test_display()} prescrite pour "
            f"{labtest.patient.nom} {labtest.patient.prenom} a été validée. "
            f"Statut : {statut_label}."
        ),
        niveau,
    )


# ── 7. Résumé patient (utilitaire) ────────────────────────────────────────────

def get_patient_lab_summary(patient):
    tests = patient.lab_tests.all()
    return {
        'total':           tests.count(),
        'en_attente':      tests.filter(status='en_attente').count(),
        'anormaux':        tests.filter(is_abnormal=True).count(),
        'critiques':       tests.filter(status='critique').count(),
        'non_interpretes': tests.filter(is_validated=True, lu_par_medecin=False).count(),
        'derniers_tests':  tests.order_by('-date_test')[:5],
    }
