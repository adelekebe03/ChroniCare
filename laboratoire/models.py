from django.db import models
from django.utils import timezone


class LabTest(models.Model):

    TYPE_TEST_CHOICES = [
        ('glycemie',      'Glycémie'),
        ('cd4',           'CD4'),
        ('charge_virale', 'Charge virale'),
        ('nfs',           'NFS / Hémogramme'),
        ('creatinine',    'Créatinine'),
        ('uree',          'Urée sanguine'),
        ('transaminases', 'Transaminases (ALAT/ASAT)'),
        ('hemoglobine',   'Hémoglobine'),
        ('cholesterol',   'Cholestérol'),
        ('tension',       'Tension artérielle'),
        ('autre',         'Autre'),
    ]

    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('normal',     'Normal'),
        ('anormal',    'Anormal'),
        ('critique',   'Critique'),
    ]

    # ── Relations principales ─────────────────────────────────────
    # suivi obligatoire : une analyse est toujours prescrite dans le cadre d'un suivi
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='lab_tests',
        verbose_name='Patient',
    )
    suivi = models.ForeignKey(
        'suivi_medical.SuiviMedical',
        on_delete=models.PROTECT,
        related_name='analyses',
        verbose_name='Suivi médical lié',
    )
    # prescripteur obligatoire : traçabilité du médecin demandeur
    prescripteur = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='analyses_prescrites',
        limit_choices_to={'role': 'doctor'},
        verbose_name='Médecin prescripteur',
    )
    technicien = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='analyses_realisees',
        verbose_name='Laborantin',
    )
    maladie = models.ForeignKey(
        'maladies.Maladie',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='lab_tests',
        verbose_name='Maladie liée',
    )

    # ── Informations de l'analyse ─────────────────────────────────
    type_test = models.CharField(
        max_length=30,
        choices=TYPE_TEST_CHOICES,
        verbose_name="Type d'analyse",
    )
    resultat = models.TextField(
        blank=True,
        verbose_name='Résultat (texte)',
    )
    unite = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Unité',
    )

    # ── Valeurs numériques ────────────────────────────────────────
    valeur           = models.FloatField(null=True, blank=True, verbose_name='Valeur mesurée')
    # valeur_secondaire : utilisée pour la diastolique (type tension)
    valeur_secondaire = models.FloatField(null=True, blank=True, verbose_name='Valeur secondaire (ex : diastolique)')
    seuil_min        = models.FloatField(null=True, blank=True, verbose_name='Seuil minimum normal')
    seuil_max        = models.FloatField(null=True, blank=True, verbose_name='Seuil maximum normal')

    # ── Statut et anomalie ────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='en_attente',
    )
    is_abnormal = models.BooleanField(default=False)
    urgence     = models.BooleanField(default=False, verbose_name='Analyse urgente')

    # ── Validation technicien ─────────────────────────────────────
    is_validated = models.BooleanField(default=False, verbose_name='Résultat validé')
    validated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='analyses_validees',
        verbose_name='Validé par',
    )
    validated_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Date de validation',
    )

    # ── Lecture médecin ───────────────────────────────────────────
    lu_par_medecin = models.BooleanField(default=False, verbose_name='Lu par le médecin')
    date_lecture   = models.DateTimeField(null=True, blank=True, verbose_name='Date de lecture')
    notes_medecin  = models.TextField(null=True, blank=True, verbose_name='Interprétation médecin')

    # ── Horodatage ────────────────────────────────────────────────
    date_test  = models.DateTimeField(auto_now_add=True, verbose_name="Date de la demande")
    updated_at = models.DateTimeField(auto_now=True,     verbose_name='Dernière mise à jour')

    class Meta:
        ordering = ['-date_test']
        verbose_name = 'Analyse de laboratoire'
        verbose_name_plural = 'Analyses de laboratoire'

    def __str__(self):
        return f"{self.patient} — {self.get_type_test_display()} ({self.date_test:%d/%m/%Y})"
