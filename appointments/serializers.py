# appointments/serializers.py

from rest_framework import serializers
from django.utils import timezone

from .models import Appointment


class AppointmentReadSerializer(serializers.ModelSerializer):

    patient_nom = serializers.SerializerMethodField()

    doctor_nom = serializers.SerializerMethodField()

    created_by_nom = serializers.SerializerMethodField()

    status_label = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:

        model = Appointment

        fields = [
            'id',

            'patient',
            'patient_nom',

            'doctor',
            'doctor_nom',

            'date',
            'heure',

            'motif',
            'notes',

            'status',
            'status_label',

            'is_reminded',

            'created_by',
            'created_by_nom',

            'created_at',
        ]

    def get_patient_nom(self, obj):

        if obj.patient:
            return f"{obj.patient.nom} {obj.patient.prenom}"

        return None

    def get_doctor_nom(self, obj):

        if obj.doctor:
            return obj.doctor.get_full_name()

        return None

    def get_created_by_nom(self, obj):

        if obj.created_by:
            return obj.created_by.get_full_name()

        return None


class AppointmentWriteSerializer(serializers.ModelSerializer):

    class Meta:

        model = Appointment

        fields = [
            'id',
            'patient',
            'doctor',
            'date',
            'heure',
            'motif',
        ]

    def validate_date(self, value):

        if value < timezone.now().date():

            raise serializers.ValidationError(
                "La date du rendez-vous ne peut pas être dans le passé."
            )

        return value


class AppointmentStatutSerializer(serializers.ModelSerializer):

    class Meta:

        model = Appointment

        fields = [
            'status',
            'notes'
        ]

    def validate_status(self, value):

        rdv = self.instance

        transitions = {

            'planifie': [
                'effectue',
                'annule'
            ],

            'effectue': [],

            'annule': [],
        }

        if value not in transitions.get(rdv.status, []):

            raise serializers.ValidationError(
                f"Transition '{rdv.status}' → '{value}' non autorisée."
            )

        return value


class AppointmentCalendarSerializer(serializers.ModelSerializer):

    title = serializers.SerializerMethodField()

    class Meta:

        model = Appointment

        fields = [
            'id',
            'title',
            'date',
            'heure',
            'status'
        ]

    def get_title(self, obj):

        return f"{obj.patient} ({obj.get_status_display()})"