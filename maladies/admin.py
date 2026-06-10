from django.contrib import admin
from .models import Maladie
from .models import SeuilAlerte
from .models import PatientMaladie
# Register your models here.

admin.site.register(Maladie)
admin.site.register(SeuilAlerte)
admin.site.register(PatientMaladie)
