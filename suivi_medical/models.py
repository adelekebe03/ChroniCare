# suivi_medical/models.py
from django.db import models


class SuiviMedical(models.Model):

    TYPE_CHOICES = (
        ('rdv',    'Avec rendez-vous'),
        ('direct', 'Sans rendez-vous'),
    )
    STATUT_CHOICES = (
        ('stable',   'Stable'),
        ('ameliore', 'Amélioré'),
        ('critique', 'Critique'),
    )

    type_suivi = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='rdv',
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suivis',
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='suivis',
    )
    medecin = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='suivis',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ── Anthropométrie ────────────────────────────────────────────
    poids  = models.FloatField(null=True, blank=True)
    taille = models.FloatField(null=True, blank=True)
    imc    = models.FloatField(null=True, blank=True, editable=False)

    # ── Cardiovasculaire ──────────────────────────────────────────
    tension_systolique  = models.IntegerField(null=True, blank=True)
    tension_diastolique = models.IntegerField(null=True, blank=True)
    cholesterol         = models.FloatField(null=True, blank=True, verbose_name='Cholestérol (g/L)')

    # ── Métabolique ───────────────────────────────────────────────
    glycemie = models.FloatField(null=True, blank=True, verbose_name='Glycémie (g/L)')

    # ── Rénal / hépatique ─────────────────────────────────────────
    creatinine    = models.FloatField(null=True, blank=True, verbose_name='Créatinine (mg/L)')
    uree          = models.FloatField(null=True, blank=True, verbose_name='Urée (g/L)')
    transaminases = models.FloatField(null=True, blank=True, verbose_name='Transaminases (UI/L)')

    # ── Hématologique ─────────────────────────────────────────────
    hemoglobine  = models.FloatField(null=True, blank=True, verbose_name='Hémoglobine (g/dL)')

    # ── VIH / immunologie ─────────────────────────────────────────
    cd4           = models.FloatField(null=True, blank=True, verbose_name='CD4 (cells/mm³)')
    charge_virale = models.FloatField(null=True, blank=True, verbose_name='Charge virale (copies/mL)')

    # ── Traçabilité des sources biologiques ───────────────────────
    # Stocke l'origine de chaque mesure : "saisie_directe" ou "analyse_labo"
    # ex : {"glycemie": "analyse_labo", "poids": "saisie_directe"}
    sources_biologiques = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Sources des mesures biologiques',
    )

    observations = models.TextField(null=True, blank=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='stable',
    )

    def save(self, *args, **kwargs):
        if self.poids and self.taille and self.taille > 0:
            self.imc = round(self.poids / ((self.taille / 100) ** 2), 2)
        else:
            self.imc = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Suivi {self.patient} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Suivi médical'
        verbose_name_plural = 'Suivis médicaux'
