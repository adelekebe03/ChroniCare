from rest_framework import serializers

from .models import (
    Medication, MedicationLot, MouvementStock,
    Prescription, PrescriptionItem,
    Dispensation, DispensationItem,
)


class MedicationSerializer(serializers.ModelSerializer):
    stock_total    = serializers.IntegerField(read_only=True)
    est_en_rupture = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Medication
        fields = ['id', 'nom', 'unite', 'stock_minimum', 'prix', 'stock_total', 'est_en_rupture']


class MedicationLotSerializer(serializers.ModelSerializer):
    medication_nom = serializers.CharField(source='medication.nom', read_only=True)
    est_expire     = serializers.BooleanField(read_only=True)

    class Meta:
        model  = MedicationLot
        fields = [
            'id', 'medication', 'medication_nom',
            'numero_lot', 'quantite', 'date_expiration', 'date_reception', 'est_expire',
        ]
        read_only_fields = ['est_expire']


class PrescriptionItemSerializer(serializers.ModelSerializer):
    medication_nom  = serializers.CharField(source='medication.nom', read_only=True)
    frequence_label = serializers.CharField(source='get_frequence_display', read_only=True)

    class Meta:
        model  = PrescriptionItem
        fields = ['id', 'medication', 'medication_nom', 'dosage', 'frequence', 'frequence_label', 'quantite']

    def validate_quantite(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0.")
        return value


class PrescriptionSerializer(serializers.ModelSerializer):
    items                      = PrescriptionItemSerializer(many=True, read_only=True)
    patient_nom                = serializers.SerializerMethodField()
    medecin_nom                = serializers.SerializerMethodField()
    maladie_nom                = serializers.SerializerMethodField()
    statut_label               = serializers.CharField(source='get_statut_display', read_only=True)
    renouvellement_proche      = serializers.BooleanField(read_only=True)
    dispensations_count        = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Prescription
        fields = [
            'id', 'patient', 'patient_nom',
            'medecin', 'medecin_nom',
            'maladie', 'maladie_nom',
            'suivi_medical',
            'statut', 'statut_label',
            'duree_standard',
            'date', 'date_prochain_renouvellement',
            'renouvellement_proche', 'dispensations_count',
            'items',
        ]
        read_only_fields = ['medecin', 'patient', 'statut', 'date', 'date_prochain_renouvellement']

    def get_patient_nom(self, obj):
        return f"{obj.patient.nom} {obj.patient.prenom}"

    def get_medecin_nom(self, obj):
        if not obj.medecin:
            return None
        return obj.medecin.get_full_name() or obj.medecin.username

    def get_maladie_nom(self, obj):
        return str(obj.maladie) if obj.maladie else None


class DispensationItemSerializer(serializers.ModelSerializer):
    medication_nom = serializers.CharField(source='medication.nom', read_only=True)
    lot_numero     = serializers.SerializerMethodField()

    class Meta:
        model  = DispensationItem
        fields = ['id', 'medication', 'medication_nom', 'lot', 'lot_numero', 'quantite']

    def get_lot_numero(self, obj):
        return obj.lot.numero_lot if obj.lot else None


class DispensationSerializer(serializers.ModelSerializer):
    prescription_patient = serializers.SerializerMethodField()
    pharmacien_nom       = serializers.SerializerMethodField()
    items                = DispensationItemSerializer(many=True, read_only=True)

    class Meta:
        model  = Dispensation
        fields = [
            'id', 'prescription', 'prescription_patient',
            'pharmacien', 'pharmacien_nom',
            'periode', 'date',
            'items',
        ]
        read_only_fields = ['pharmacien', 'date', 'periode']

    def get_prescription_patient(self, obj):
        p = obj.prescription.patient
        return f"{p.nom} {p.prenom}"

    def get_pharmacien_nom(self, obj):
        if not obj.pharmacien:
            return None
        return obj.pharmacien.get_full_name() or obj.pharmacien.username


class MouvementStockSerializer(serializers.ModelSerializer):
    medication_nom       = serializers.CharField(source='lot.medication.nom', read_only=True)
    type_mouvement_label = serializers.CharField(source='get_type_mouvement_display', read_only=True)
    utilisateur_nom      = serializers.SerializerMethodField()

    class Meta:
        model  = MouvementStock
        fields = [
            'id', 'lot', 'medication_nom',
            'type_mouvement', 'type_mouvement_label',
            'quantite', 'date',
            'utilisateur', 'utilisateur_nom',
            'dispensation', 'reference',
        ]
        read_only_fields = ['date']

    def get_utilisateur_nom(self, obj):
        if not obj.utilisateur:
            return None
        return obj.utilisateur.get_full_name() or obj.utilisateur.username
