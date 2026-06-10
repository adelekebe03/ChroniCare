from rest_framework import serializers
from .models import LabTest


class LabTestSerializer(serializers.ModelSerializer):

    patient_nom      = serializers.SerializerMethodField()
    prescripteur_nom = serializers.SerializerMethodField()
    technicien_nom   = serializers.SerializerMethodField()
    validated_by_nom = serializers.SerializerMethodField()
    statut_label     = serializers.CharField(source='get_status_display', read_only=True)
    type_test_label  = serializers.CharField(source='get_type_test_display', read_only=True)
    suivi_date       = serializers.DateTimeField(source='suivi.created_at', read_only=True)

    class Meta:
        model = LabTest
        fields = [
            'id',
            'patient',      'patient_nom',
            'suivi',        'suivi_date',
            'prescripteur', 'prescripteur_nom',
            'technicien',   'technicien_nom',
            'maladie',

            'type_test',    'type_test_label',
            'urgence',
            'resultat',
            'unite',
            'valeur',
            'valeur_secondaire',
            'seuil_min',
            'seuil_max',

            'status',       'statut_label',
            'is_abnormal',

            'is_validated',
            'validated_by', 'validated_by_nom',
            'validated_at',

            'lu_par_medecin',
            'date_lecture',
            'notes_medecin',

            'date_test',
            'updated_at',
        ]
        read_only_fields = [
            # Relations immuables après création
            'prescripteur',
            'patient',
            'suivi',
            # Champs calculés automatiquement
            'is_abnormal',
            'status',
            # Workflow de validation (géré uniquement par l'action valider)
            'is_validated',
            'validated_by', 'validated_at',
            # Workflow de lecture médecin (géré uniquement par labtest_mark_interpreted)
            'lu_par_medecin',
            'date_lecture',
            # Horodatage automatique
            'date_test', 'updated_at',
            # Champs calculés du serializer
            'statut_label', 'type_test_label', 'suivi_date',
            'technicien_nom', 'validated_by_nom',
            'patient_nom', 'prescripteur_nom',
        ]

    def get_patient_nom(self, obj):
        return f"{obj.patient.nom} {obj.patient.prenom}"

    def get_prescripteur_nom(self, obj):
        if obj.prescripteur_id:
            name = obj.prescripteur.get_full_name()
            return f"Dr. {name or obj.prescripteur.username}"
        return None

    def get_technicien_nom(self, obj):
        if obj.technicien_id:
            return obj.technicien.get_full_name() or obj.technicien.username
        return None

    def get_validated_by_nom(self, obj):
        if obj.validated_by_id:
            return obj.validated_by.get_full_name() or obj.validated_by.username
        return None

    def validate_notes_medecin(self, value):
        """Seuls le médecin et l'admin peuvent écrire l'interprétation."""
        request = self.context.get('request')
        if value and request:
            role = getattr(request.user, 'role', None)
            if role not in ('doctor', 'admin'):
                raise serializers.ValidationError(
                    "Seul le médecin prescripteur peut renseigner l'interprétation."
                )
        return value
