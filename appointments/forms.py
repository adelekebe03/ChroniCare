from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):

    class Meta:

        model = Appointment

        fields = [
            'patient',
            'doctor',
            'date',
            'heure',
            'motif',
            'notes',
            'status',
        ]

        widgets = {

            'date': forms.DateInput(
                  attrs={'type': 'date'}
            ),

            'heure': forms.TimeInput(
                attrs={'type': 'time'}
            ),

        }