from django import forms
from django.forms import inlineformset_factory
from .models import Maladie, PatientMaladie, SeuilAlerte

class MaladieForm(forms.ModelForm):

    class Meta:
        model = Maladie
        fields = ['nom', 'type', 'description']

        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PatientMaladieForm(forms.ModelForm):
    class Meta:
        model = PatientMaladie
        fields = ['patient', 'maladie', 'status', 'date_diagnostic', 'observations']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'maladie': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'date_diagnostic': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


class PatientMaladieUpdateForm(forms.ModelForm):
    """Formulaire de modification : patient et maladie verrouillés."""
    class Meta:
        model = PatientMaladie
        fields = ['status', 'date_diagnostic', 'observations']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'date_diagnostic': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


SeuilAlerteFormSet = inlineformset_factory(
    PatientMaladie,
    SeuilAlerte,
    fields=['indicateur', 'min_valeur', 'max_valeur'],
    extra=1,
    can_delete=True,
    widgets={
        'indicateur': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ex : Glycémie, CD4, Tension systolique…',
        }),
        'min_valeur': forms.NumberInput(attrs={
            'class': 'form-control', 'step': '0.01', 'placeholder': 'Min',
        }),
        'max_valeur': forms.NumberInput(attrs={
            'class': 'form-control', 'step': '0.01', 'placeholder': 'Max',
        }),
    }
)