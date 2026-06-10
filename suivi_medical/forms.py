from django import forms
from django.contrib.auth import get_user_model
from .models import SuiviMedical
from appointments.models import Appointment

User = get_user_model()

_VITAL_WIDGETS = {
    "poids": forms.NumberInput(attrs={
        "class": "form-control", "step": "0.1", "placeholder": "ex : 75.5",
        "id": "id_poids",
    }),
    "taille": forms.NumberInput(attrs={
        "class": "form-control", "step": "0.01",
        "placeholder": "ex : 1.70 ou 170",
        "id": "id_taille",
    }),
    "tension_systolique": forms.NumberInput(attrs={
        "class": "form-control", "placeholder": "ex : 12",
    }),
    "tension_diastolique": forms.NumberInput(attrs={
        "class": "form-control", "placeholder": "ex : 8",
    }),
    "glycemie": forms.NumberInput(attrs={
        "class": "form-control", "step": "0.01", "placeholder": "g/L",
    }),
    "cd4": forms.NumberInput(attrs={
        "class": "form-control", "step": "1", "placeholder": "cells/mm³",
    }),
    "charge_virale": forms.NumberInput(attrs={
        "class": "form-control", "step": "1", "placeholder": "copies/mL",
    }),
    # Nouveaux champs biologiques
    "cholesterol": forms.NumberInput(attrs={
        "class": "form-control", "step": "0.01", "placeholder": "g/L",
    }),
    "creatinine": forms.NumberInput(attrs={
        "class": "form-control", "step": "0.1", "placeholder": "mg/L",
    }),
    "uree": forms.NumberInput(attrs={
        "class": "form-control", "step": "0.01", "placeholder": "g/L",
    }),
    "transaminases": forms.NumberInput(attrs={
        "class": "form-control", "step": "1", "placeholder": "UI/L",
    }),
    "hemoglobine": forms.NumberInput(attrs={
        "class": "form-control", "step": "0.1", "placeholder": "g/dL",
    }),
    "observations": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    "statut": forms.Select(attrs={"class": "form-control"}),
}


def _normalise_taille(taille):
    """Convertit les cm en m si la valeur dépasse 3."""
    if taille is None:
        return taille
    if taille > 3:
        taille = round(taille / 100, 2)
    return taille


class SuiviMedicalCreateForm(forms.ModelForm):
    """Formulaire de création — supporte RDV et consultation directe."""

    class Meta:
        model = SuiviMedical
        fields = [
            "type_suivi", "appointment", "patient", "medecin",
            "poids", "taille",
            "tension_systolique", "tension_diastolique",
            "glycemie",
            "cholesterol", "creatinine", "uree", "transaminases", "hemoglobine",
            "cd4", "charge_virale",
            "observations", "statut",
        ]
        widgets = {
            "type_suivi": forms.Select(attrs={
                "class": "form-control", "id": "id_type_suivi",
            }),
            "appointment": forms.Select(attrs={"class": "form-control"}),
            "patient": forms.Select(attrs={"class": "form-control"}),
            "medecin": forms.Select(attrs={"class": "form-control"}),
            **_VITAL_WIDGETS,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["appointment"].queryset = (
            Appointment.objects.select_related("patient", "doctor")
            .filter(status="planifie")
        )
        self.fields["appointment"].required = False
        self.fields["patient"].required = False
        self.fields["medecin"].queryset = User.objects.filter(role="doctor")
        self.fields["medecin"].required = False

    def clean_taille(self):
        return _normalise_taille(self.cleaned_data.get("taille"))

    def clean(self):
        cd = super().clean()
        type_suivi = cd.get("type_suivi")
        if type_suivi == "rdv" and not cd.get("appointment"):
            self.add_error("appointment", "Sélectionnez un rendez-vous.")
        if type_suivi == "direct" and not cd.get("patient"):
            self.add_error("patient", "Sélectionnez un patient.")
        return cd


class SuiviMedicalUpdateForm(forms.ModelForm):
    """Formulaire de modification — vitaux et observations seulement."""

    class Meta:
        model = SuiviMedical
        fields = [
            "poids", "taille",
            "tension_systolique", "tension_diastolique",
            "glycemie",
            "cholesterol", "creatinine", "uree", "transaminases", "hemoglobine",
            "cd4", "charge_virale",
            "observations", "statut",
        ]
        widgets = _VITAL_WIDGETS

    def clean_taille(self):
        return _normalise_taille(self.cleaned_data.get("taille"))


# Alias rétro-compatible
SuiviMedicalForm = SuiviMedicalCreateForm
