from django import forms
from .models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()


class PatientForm(forms.ModelForm):

    class Meta:
        model = Patient
        fields = [
            "compte_patient",
            "nom",
            "prenom",
            "date_naissance",
            "sexe",
            "telephone",
            "groupe_sanguin",
            "contact_urgence",
            "adresse",
            "assurance",
            "antecedents_personnels",
            "antecedents_familiaux",
            "medecin_traitant",
        ]
        widgets = {
            "compte_patient": forms.Select(attrs={"class": "form-select"}),
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "prenom": forms.TextInput(attrs={"class": "form-control"}),
            "date_naissance": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "sexe": forms.Select(attrs={"class": "form-select"}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
            "groupe_sanguin": forms.Select(attrs={"class": "form-select"}),
            "contact_urgence": forms.TextInput(attrs={"class": "form-control"}),
            "adresse": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "assurance": forms.TextInput(attrs={"class": "form-control"}),
            "antecedents_personnels": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "antecedents_familiaux": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "medecin_traitant": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Exclure les utilisateurs déjà liés à un autre patient (contrainte OneToOne)
        already_linked = User.objects.filter(profil_patient__isnull=False)
        if self.instance and self.instance.pk and self.instance.compte_patient_id:
            already_linked = already_linked.exclude(pk=self.instance.compte_patient_id)
        self.fields['compte_patient'].queryset = User.objects.filter(role='patient').exclude(
            pk__in=already_linked
        )
        self.fields['compte_patient'].required = False

        self.fields['medecin_traitant'].queryset = User.objects.filter(role='doctor')
