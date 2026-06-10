

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Infos médicales", {
            "fields": ("role", "photo", "specialite", "contact")
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Infos médicales", {
            "fields": ("role", "photo", "specialite", "contact")
        }),
    )


admin.site.register(User, CustomUserAdmin)
