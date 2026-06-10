from django.db import models
from django.utils import timezone
from datetime import timedelta


class Medication(models.Model):

    UNITE_CHOICES = (
        ('comprime',  'Comprimé'),
        ('gelule',    'Gélule'),
        ('sirop',     'Sirop'),
        ('injection', 'Injection'),
        ('autre',     'Autre'),
    )

    nom           = models.CharField(max_length=100, verbose_name='Nom')
    unite         = models.CharField(max_length=20, choices=UNITE_CHOICES, default='comprime', verbose_name='Forme')
    stock_minimum = models.IntegerField(default=5, verbose_name='Seuil d\'alerte')
    prix          = models.FloatField(default=0, verbose_name='Prix unitaire')

    class Meta:
        ordering = ['nom']
        verbose_name = 'Médicament'
        verbose_name_plural = 'Médicaments'

    def __str__(self):
        return self.nom

    @property
    def stock_total(self):
        """Stock disponible : lots non expirés uniquement."""
        return (
            self.lots
            .filter(date_expiration__gt=timezone.now().date(), quantite__gt=0)
            .aggregate(total=models.Sum('quantite'))['total'] or 0
        )

    @property
    def est_en_rupture(self):
        return self.stock_total <= self.stock_minimum


class MedicationLot(models.Model):

    medication      = models.ForeignKey(
        'Medication', on_delete=models.CASCADE, related_name='lots',
        verbose_name='Médicament',
    )
    numero_lot      = models.CharField(max_length=100, unique=True, blank=True, verbose_name='N° de lot')
    quantite        = models.IntegerField(verbose_name='Quantité en stock')
    date_expiration = models.DateField(verbose_name='Date d\'expiration')
    date_reception  = models.DateField(default=timezone.now, verbose_name='Date de réception')

    class Meta:
        ordering = ['date_expiration']
        verbose_name = 'Lot'
        verbose_name_plural = 'Lots'

    def __str__(self):
        return f"{self.medication.nom} — {self.numero_lot}"

    @property
    def est_expire(self):
        return self.date_expiration < timezone.now().date()


class Prescription(models.Model):

    STATUT_CHOICES = (
        ('en_attente', 'En attente'),
        ('active',     'Active'),
        ('terminee',   'Terminée'),
        ('annulee',    'Annulée'),
    )

    FREQUENCE_CHOICES = (
        (30,  '1 mois'),
        (60,  '2 mois'),
        (90,  '3 mois'),
        (180, '6 mois'),
    )

    suivi_medical = models.ForeignKey(
        'suivi_medical.SuiviMedical',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='prescriptions',
        verbose_name='Suivi médical',
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name='Patient',
    )
    medecin = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='prescriptions',
        limit_choices_to={'role': 'doctor'},
        verbose_name='Médecin prescripteur',
    )
    maladie = models.ForeignKey(
        'maladies.Maladie',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='prescriptions',
        verbose_name='Maladie chronique concernée',
    )

    statut          = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name='Statut')
    date            = models.DateTimeField(auto_now_add=True, verbose_name='Date de prescription')
    duree_standard  = models.IntegerField(choices=FREQUENCE_CHOICES, default=30, verbose_name='Fréquence de renouvellement')
    date_prochain_renouvellement = models.DateField(null=True, blank=True, verbose_name='Prochain renouvellement')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'

    def save(self, *args, **kwargs):
        if not self.date_prochain_renouvellement:
            self.date_prochain_renouvellement = (
                timezone.now().date() + timedelta(days=self.duree_standard)
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Prescription {self.patient} — {self.date:%d/%m/%Y}"

    @property
    def renouvellement_proche(self):
        """Vrai si le renouvellement est dans les 7 prochains jours."""
        if not self.date_prochain_renouvellement:
            return False
        return (self.date_prochain_renouvellement - timezone.now().date()).days <= 7

    @property
    def dispensations_count(self):
        return self.dispensations.count()


class PrescriptionItem(models.Model):

    FREQUENCE_CHOICES = (
        ('1_par_jour',  '1 fois par jour'),
        ('2_par_jour',  '2 fois par jour'),
        ('3_par_jour',  '3 fois par jour'),
        ('1_par_semaine', '1 fois par semaine'),
        ('au_besoin',   'Au besoin'),
    )

    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name='items',
        verbose_name='Prescription',
    )
    medication = models.ForeignKey(
        Medication, on_delete=models.CASCADE,
        verbose_name='Médicament',
    )
    dosage    = models.CharField(max_length=100, verbose_name='Dosage')
    frequence = models.CharField(max_length=30, choices=FREQUENCE_CHOICES, default='1_par_jour', verbose_name='Fréquence')
    quantite  = models.IntegerField(default=1, verbose_name='Quantité par dispensation')

    def __str__(self):
        return f"{self.medication.nom} — {self.dosage}"


class Dispensation(models.Model):
    """Une dispensation = un acte physique de remise de médicaments pour une période donnée."""

    # ForeignKey (pas OneToOne) : plusieurs dispensations possibles par prescription (renouvellements)
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.PROTECT,
        related_name='dispensations',
        verbose_name='Prescription',
    )
    pharmacien = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'pharmacist'},
        related_name='dispensations_realisees',
        verbose_name='Pharmacien',
    )
    # Période de dispensation (1er jour du mois de délivrance) — clé d'unicité pour les renouvellements
    periode      = models.DateField(null=True, blank=True, verbose_name='Période (mois)')
    date         = models.DateTimeField(auto_now_add=True, verbose_name='Date de dispensation')
    cachet_pharmacie = models.ImageField(upload_to='cachets/', null=True, blank=True, verbose_name='Cachet pharmacie')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Dispensation'
        verbose_name_plural = 'Dispensations'
        # Une seule dispensation par prescription et par période
        constraints = [
            models.UniqueConstraint(
                fields=['prescription', 'periode'],
                name='unique_dispensation_par_periode',
            )
        ]

    def __str__(self):
        return f"Dispensation — {self.prescription.patient} ({self.periode})"


class DispensationItem(models.Model):

    dispensation = models.ForeignKey(
        Dispensation, on_delete=models.CASCADE, related_name='items',
        verbose_name='Dispensation',
    )
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, verbose_name='Médicament')
    lot        = models.ForeignKey(MedicationLot, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Lot')
    quantite   = models.IntegerField(verbose_name='Quantité délivrée')

    def __str__(self):
        return f"{self.medication.nom} — {self.quantite}"


class MouvementStock(models.Model):
    """Audit trail de chaque entrée / sortie de stock."""

    TYPE_CHOICES = [
        ('reception',    'Réception'),
        ('dispensation', 'Dispensation'),
        ('peremption',   'Péremption / ajustement'),
    ]

    lot            = models.ForeignKey(MedicationLot, on_delete=models.PROTECT, related_name='mouvements', verbose_name='Lot')
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Type')
    quantite       = models.IntegerField(verbose_name='Quantité (+ entrée / − sortie)')
    date           = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    utilisateur    = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True,
        related_name='mouvements_stock', verbose_name='Utilisateur',
    )
    dispensation   = models.ForeignKey(
        Dispensation, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mouvements', verbose_name='Dispensation liée',
    )
    reference      = models.CharField(max_length=200, blank=True, verbose_name='Référence')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'

    def __str__(self):
        signe = '+' if self.quantite > 0 else ''
        return f"{self.lot.medication.nom} {signe}{self.quantite} ({self.get_type_mouvement_display()})"
