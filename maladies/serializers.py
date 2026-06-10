from rest_framework import serializers
from .models import Maladie, PatientMaladie, SeuilAlerte


class MaladieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Maladie
        fields = '__all__'


class PatientMaladieSerializer(serializers.ModelSerializer):

    patient_nom = serializers.SerializerMethodField()
    maladie_nom = serializers.CharField(source='maladie.nom', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PatientMaladie
        fields = [
            'id',
            'patient',
            'patient_nom',
            'maladie',
            'maladie_nom',
            'status',
            'status_label',
            'date_diagnostic',
            'observations'
        ]

    def get_patient_nom(self, obj):
        return f"{obj.patient.nom} {obj.patient.prenom}"


class SeuilAlerteSerializer(serializers.ModelSerializer):

    patient_maladie_info = serializers.SerializerMethodField()

    class Meta:
        model = SeuilAlerte
        fields = [
            'id',
            'patient_maladie',
            'patient_maladie_info',
            'indicateur',
            'min_valeur',
            'max_valeur'
        ]

    def get_patient_maladie_info(self, obj):
        return f"{obj.patient_maladie.patient.nom} - {obj.patient_maladie.maladie.nom}"            
    