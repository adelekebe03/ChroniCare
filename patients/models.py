from django.db import models
from django.conf import settings


class Patient(models.Model):

    SEXE_CHOICES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )
    GROUPE_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    )

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='patients_crees',
    )

    compte_patient = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='profil_patient',
        limit_choices_to={'role': 'patient'},
    )

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)

    date_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    telephone = models.CharField(max_length=20)
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_CHOICES)
    contact_urgence = models.CharField(max_length=20)

    adresse = models.TextField(null=True, blank=True)
    assurance = models.CharField(max_length=100, null=True, blank=True)
    antecedents_personnels = models.TextField(null=True, blank=True)
    antecedents_familiaux = models.TextField(null=True, blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    medecin_traitant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients_suivis',
        limit_choices_to={'role': 'doctor'},
    )

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
