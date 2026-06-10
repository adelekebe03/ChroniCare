from django.contrib import admin

from .models import (
    Medication, MedicationLot, MouvementStock,
    Prescription, PrescriptionItem,
    Dispensation, DispensationItem,
)


class PrescriptionItemInline(admin.TabularInline):
    model  = PrescriptionItem
    extra  = 0


class DispensationItemInline(admin.TabularInline):
    model  = DispensationItem
    extra  = 0
    readonly_fields = ['lot', 'medication', 'quantite']


class MouvementStockInline(admin.TabularInline):
    model           = MouvementStock
    extra           = 0
    readonly_fields = ['lot', 'type_mouvement', 'quantite', 'date', 'utilisateur', 'dispensation', 'reference']
    can_delete      = False


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'unite', 'stock_total', 'stock_minimum', 'est_en_rupture', 'prix']
    list_filter   = ['unite']
    search_fields = ['nom']

    @admin.display(boolean=True, description='Rupture ?')
    def est_en_rupture(self, obj):
        return obj.est_en_rupture


@admin.register(MedicationLot)
class MedicationLotAdmin(admin.ModelAdmin):
    list_display  = ['medication', 'numero_lot', 'quantite', 'date_expiration', 'date_reception', 'est_expire']
    list_filter   = ['medication']
    search_fields = ['numero_lot', 'medication__nom']
    inlines       = [MouvementStockInline]

    @admin.display(boolean=True, description='Expiré ?')
    def est_expire(self, obj):
        return obj.est_expire


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display  = ['patient', 'medecin', 'maladie', 'statut', 'duree_standard', 'date_prochain_renouvellement', 'renouvellement_proche']
    list_filter   = ['statut', 'duree_standard', 'maladie']
    search_fields = ['patient__nom', 'patient__prenom', 'medecin__first_name', 'medecin__last_name']
    inlines       = [PrescriptionItemInline]
    readonly_fields = ['date', 'statut']

    @admin.display(boolean=True, description='Renouvellement proche ?')
    def renouvellement_proche(self, obj):
        return obj.renouvellement_proche


@admin.register(Dispensation)
class DispensationAdmin(admin.ModelAdmin):
    list_display  = ['prescription', 'pharmacien', 'periode', 'date']
    list_filter   = ['periode']
    search_fields = ['prescription__patient__nom']
    inlines       = [DispensationItemInline, MouvementStockInline]
    readonly_fields = ['date', 'pharmacien', 'periode', 'prescription']


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display  = ['lot', 'type_mouvement', 'quantite', 'date', 'utilisateur', 'reference']
    list_filter   = ['type_mouvement']
    search_fields = ['lot__medication__nom', 'reference']
    readonly_fields = ['date']
