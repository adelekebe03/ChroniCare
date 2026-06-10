from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime


class Appointment(models.Model):

    STATUS_CHOICES = (
        ('planifie', 'Planifié'),
        ('effectue', 'Effectué'),
        ('annule', 'Annulé'),
    )

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    doctor = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'doctor'}
    )

    date = models.DateField()

    heure = models.TimeField()

    motif = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    notes = models.TextField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planifie'
    )

    is_reminded = models.BooleanField(
        default=False
    )

    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_appointments'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def clean(self):

        # éviter crash si champs vides
        if not self.date or not self.heure:
            return

        # fusion date + heure
        appointment_datetime = datetime.combine(
            self.date,
            self.heure
        )

        appointment_datetime = timezone.make_aware(
            appointment_datetime
        )

        # rendez-vous passé
        if appointment_datetime < timezone.now():

            raise ValidationError(
                "La date du rendez-vous ne peut pas être dans le passé."
            )

        # conflit médecin
        if Appointment.objects.filter(
            doctor=self.doctor,
            date=self.date,
            heure=self.heure
        ).exclude(
            id=self.id
        ).exclude(
            status='annule'
        ).exists():

            raise ValidationError(
                "Ce médecin a déjà un rendez-vous à cette heure."
            )

        # conflit patient
        if Appointment.objects.filter(
            patient=self.patient,
            date=self.date,
            heure=self.heure
        ).exclude(
            id=self.id
        ).exclude(
            status='annule'
        ).exists():

            raise ValidationError(
                "Ce patient a déjà un rendez-vous à cette heure."
            )

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.patient} — {self.date} {self.heure}"

    class Meta:

        ordering = ['date', 'heure']

        verbose_name = 'Rendez-vous'

        verbose_name_plural = 'Rendez-vous'

        constraints = [

            models.UniqueConstraint(
                fields=['doctor', 'date', 'heure'],
                name='unique_doctor_appointment'
            ),

            models.UniqueConstraint(
                fields=['patient', 'date', 'heure'],
                name='unique_patient_appointment'
            ),
        ]

