from django.contrib import admin
from .models import LabTest


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display  = ('patient', 'type_test', 'status', 'urgence', 'is_validated', 'date_test')
    list_filter   = ('status', 'type_test', 'urgence', 'is_validated')
    search_fields = ('patient__nom', 'patient__prenom', 'prescripteur__username')
    readonly_fields = (
        'prescripteur', 'validated_by', 'validated_at',
        'date_test', 'updated_at', 'technicien',
    )
    # suivi obligatoire : le champ reste éditable pour corriger les données admin uniquement
    autocomplete_fields = []

    def get_readonly_fields(self, request, obj=None):
        ro = list(self.readonly_fields)
        if obj:
            # Une fois créé, suivi et prescripteur ne peuvent plus changer
            ro += ['suivi', 'patient']
        return ro

    def has_add_permission(self, request):
        # L'admin peut créer (cas exceptionnel) mais est guidé par les readonly
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        # Injection automatique du prescripteur si création via admin
        if not change and not obj.prescripteur_id:
            obj.prescripteur = request.user
        super().save_model(request, obj, form, change)
