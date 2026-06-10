from django.contrib import admin
from .models import Appointment
# Register your models here.
# appointments/admin.py


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ['patient', 'doctor', 'date', 'heure', 'status', 'is_reminded']
    list_filter   = ['status', 'date', 'is_reminded']
    search_fields = ['patient__nom', 'patient__prenom', 'doctor__last_name']
    ordering      = ['date', 'heure']
