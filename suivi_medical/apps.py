from django.apps import AppConfig


class SuiviMedicalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'suivi_medical'

    def ready(self):
          import suivi_medical.signals
