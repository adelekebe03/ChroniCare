from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone


class Notification(models.Model):
    """Notification interne destinée à un utilisateur du système (médecin, infirmier, pharmacien…)."""

    LEVEL_CHOICES = [
        ('info',    'Information'),
        ('warning', 'Avertissement'),
        ('urgent',  'Urgent'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinataire',
    )
    # Lien optionnel vers un rendez-vous (ON_DELETE=SET_NULL : ne supprime pas la notif si RDV supprimé)
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='notifications',
        verbose_name='Rendez-vous lié',
    )
    title   = models.CharField(max_length=255, verbose_name='Titre')
    message = models.TextField(verbose_name='Message')
    level   = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='info', verbose_name='Niveau')
    is_read = models.BooleanField(default=False, verbose_name='Lu')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"[{self.get_level_display()}] {self.title} → {self.user}"


class Alert(models.Model):
    """
    Alerte médicale générée automatiquement lors d'un dépassement de seuil
    (glycémie, tension, résultat labo, stock pharmacie…).

    Cycle de vie : non résolue → accusée (par médecin) → résolue.
    """

    ALERT_TYPE_CHOICES = [
        ('critical', 'Critique'),
        ('warning',  'Avertissement'),
        ('info',     'Information'),
    ]

    SOURCE_CHOICES = [
        ('suivi_medical',  'Suivi médical'),
        ('laboratoire',    'Laboratoire'),
        ('stock_pharmacie','Stock pharmacie'),
        ('renouvellement', 'Renouvellement traitement'),
        ('rdv',            'Rendez-vous'),
        ('system',         'Système'),
    ]

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name='Patient',
    )
    alert_type = models.CharField(
        max_length=20, choices=ALERT_TYPE_CHOICES, default='warning',
        verbose_name='Sévérité',
    )
    source = models.CharField(
        max_length=50, choices=SOURCE_CHOICES, default='system',
        verbose_name='Source',
    )
    message = models.TextField(verbose_name='Message')

    # Liens vers les données sources (traçabilité)
    source_suivi = models.ForeignKey(
        'suivi_medical.SuiviMedical',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertes',
        verbose_name='Suivi médical lié',
    )
    source_labtest = models.ForeignKey(
        'laboratoire.LabTest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertes',
        verbose_name='Analyse liée',
    )

    is_resolved   = models.BooleanField(default=False, verbose_name='Résolue')
    resolved_at   = models.DateTimeField(null=True, blank=True, verbose_name='Résolue le')
    resolved_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertes_resolues',
        verbose_name='Résolue par',
    )

    # Accusé de réception médecin (avant résolution)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alertes_accusees',
        verbose_name='Accusée par',
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name='Accusée le')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créée le')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Alerte médicale'
        verbose_name_plural = 'Alertes médicales'

    def __str__(self):
        return f"[{self.get_alert_type_display()}] {self.patient} — {self.source}"

    @property
    def is_acknowledged(self):
        return self.acknowledged_by is not None

    def acknowledge(self, user):
        """Accusé de réception : le médecin confirme avoir vu l'alerte."""
        if not self.acknowledged_by:
            self.acknowledged_by = user
            self.acknowledged_at = timezone.now()
            self.save(update_fields=['acknowledged_by', 'acknowledged_at'])

    def resolve(self, user):
        """Résolution : l'alerte est traitée."""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save(update_fields=['is_resolved', 'resolved_at', 'resolved_by'])


class MessageTemplate(models.Model):
    """
    Template de message réutilisable.
    Supporte les variables {{patient_nom}}, {{valeur}}, {{seuil}}, {{unite}}, {{date}}.
    """

    TYPE_CHOICES = [
        ('alert',        'Alerte'),
        ('notification', 'Notification'),
        ('info',         'Information'),
        ('warning',      'Avertissement'),
    ]

    title   = models.CharField(max_length=255, verbose_name='Titre')
    content = models.TextField(verbose_name='Contenu (variables: {{patient_nom}}, {{valeur}}, {{seuil}}, {{unite}}, {{date}})')
    type    = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info', verbose_name='Type')
    code    = models.SlugField(unique=True, blank=True, verbose_name='Code unique')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Modèle de message'
        verbose_name_plural = 'Modèles de messages'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.title)
        super().save(*args, **kwargs)  # toujours appelé

    def render(self, context: dict) -> str:
        """Remplace les variables du template par les valeurs du contexte."""
        content = self.content
        for key, value in context.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        return content

    def __str__(self):
        return f"{self.title} [{self.code}]"
