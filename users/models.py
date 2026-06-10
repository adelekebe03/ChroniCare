from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):

    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('doctor', 'Médecin'),
        ('nurse', 'Infirmier(e)'),
        ('patient', 'Patient'),
        ('pharmacist', 'Pharmacien'),
        ('lab', 'Laboratoire'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='patient'
    )

    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    specialite = models.CharField(max_length=100, null=True, blank=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    signature = models.ImageField(upload_to="signatures/", null=True, blank=True)

    is_active_status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.role == 'doctor' and not self.specialite:
            raise ValidationError("Un médecin doit avoir une spécialité")

    def is_doctor(self):
        return self.role == 'doctor'

    def is_admin(self):
        return self.role == 'admin'

    def is_patient(self):
        return self.role == 'patient'

    def is_pharmacist(self):
        return self.role == 'pharmacist'

    def is_lab(self):
        return self.role == 'lab'

    def is_nurse(self):
        return self.role == 'nurse'

    def __str__(self):
        return self.username
