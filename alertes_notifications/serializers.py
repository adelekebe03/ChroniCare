from rest_framework import serializers

from .models import Alert, Notification, MessageTemplate


class AlertSerializer(serializers.ModelSerializer):
    patient_nom         = serializers.SerializerMethodField()
    alert_type_label    = serializers.CharField(source='get_alert_type_display', read_only=True)
    source_label        = serializers.CharField(source='get_source_display', read_only=True)
    acknowledged_by_nom = serializers.SerializerMethodField()
    resolved_by_nom     = serializers.SerializerMethodField()
    is_acknowledged     = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Alert
        fields = [
            'id', 'patient', 'patient_nom',
            'alert_type', 'alert_type_label',
            'source', 'source_label',
            'message',
            'source_suivi', 'source_labtest',
            'is_resolved', 'resolved_at', 'resolved_by', 'resolved_by_nom',
            'is_acknowledged', 'acknowledged_at', 'acknowledged_by', 'acknowledged_by_nom',
            'created_at',
        ]
        read_only_fields = [
            'is_resolved', 'resolved_at', 'resolved_by',
            'acknowledged_by', 'acknowledged_at',
            'created_at',
        ]

    def get_patient_nom(self, obj):
        return f"{obj.patient.prenom} {obj.patient.nom}"

    def get_acknowledged_by_nom(self, obj):
        if not obj.acknowledged_by:
            return None
        return obj.acknowledged_by.get_full_name() or obj.acknowledged_by.username

    def get_resolved_by_nom(self, obj):
        if not obj.resolved_by:
            return None
        return obj.resolved_by.get_full_name() or obj.resolved_by.username


class NotificationSerializer(serializers.ModelSerializer):
    user_nom    = serializers.SerializerMethodField()
    level_label = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model  = Notification
        fields = [
            'id', 'user', 'user_nom',
            'title', 'message',
            'level', 'level_label',
            'is_read', 'created_at',
            'appointment',
        ]
        read_only_fields = ['user', 'created_at']

    def get_user_nom(self, obj):
        return obj.user.get_full_name() or obj.user.username


class MessageTemplateSerializer(serializers.ModelSerializer):
    type_label = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model  = MessageTemplate
        fields = ['id', 'title', 'content', 'type', 'type_label', 'code', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
