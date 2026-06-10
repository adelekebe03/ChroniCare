from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['cree_par']

    def validate_medecin_traitant(self, value):
        if value and getattr(value, "role", None) != 'doctor':
            raise serializers.ValidationError(
                "Le médecin traitant doit avoir le rôle doctor"
            )
        return value

    def validate_compte_patient(self, value):
        if value and getattr(value, "role", None) != 'patient':
            raise serializers.ValidationError(
                "Le compte doit être un utilisateur avec rôle patient"
            )
        return value
