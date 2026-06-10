from django import forms
from .models import LabTest
from .services import TYPE_TEST_DEFAULTS


class LabTestCreateForm(forms.ModelForm):
    """
    Formulaire médecin — prescription d'une analyse depuis un suivi médical.
    Les champs patient, suivi, prescripteur sont injectés par la vue.
    """

    class Meta:
        model = LabTest
        fields = ['type_test', 'urgence', 'seuil_min', 'seuil_max', 'maladie']
        widgets = {
            'type_test': forms.Select(attrs={
                'class': 'form-control', 'id': 'id_type_test',
            }),
            'urgence': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seuil_min': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': 'Min',
            }),
            'seuil_max': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'placeholder': 'Max',
            }),
            'maladie': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, suivi=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seuil_min'].required = False
        self.fields['seuil_max'].required = False
        self.fields['maladie'].required = False
        # Suggère les maladies du patient en premier
        if suivi:
            try:
                from maladies.models import Maladie, PatientMaladie
                patient_maladie_ids = PatientMaladie.objects.filter(
                    patient=suivi.patient
                ).values_list('maladie_id', flat=True)
                if patient_maladie_ids:
                    self.fields['maladie'].queryset = Maladie.objects.filter(
                        id__in=patient_maladie_ids
                    )
            except Exception:
                pass


class LabTestResultForm(forms.ModelForm):
    """
    Formulaire technicien — saisie du résultat d'une analyse.
    status est calculé automatiquement par la vue.
    """

    class Meta:
        model = LabTest
        fields = ['valeur', 'valeur_secondaire', 'unite', 'resultat']
        widgets = {
            'valeur': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.001',
                'id': 'id_valeur', 'placeholder': 'Valeur numérique (ex : systolique)',
            }),
            'valeur_secondaire': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.001',
                'id': 'id_valeur_secondaire',
                'placeholder': 'Valeur diastolique (tension uniquement)',
            }),
            'unite': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'ex : g/L',
            }),
            'resultat': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Description textuelle du résultat…',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valeur'].required = False
        self.fields['valeur_secondaire'].required = False
        self.fields['unite'].required = False
        self.fields['resultat'].required = False


class LabTestInterpretForm(forms.ModelForm):
    """
    Formulaire médecin — interprétation et annotation d'un résultat validé.
    lu_par_medecin et date_lecture sont injectés par la vue.
    """

    class Meta:
        model = LabTest
        fields = ['notes_medecin']
        widgets = {
            'notes_medecin': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5,
                'placeholder': (
                    'Interprétation clinique, conduite à tenir, '
                    'adaptation thérapeutique…'
                ),
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes_medecin'].required = False
