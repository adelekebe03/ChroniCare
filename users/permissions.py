from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "doctor"


class IsNurse(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "nurse"


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "patient"


class IsPharmacist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "pharmacist"


class IsLab(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "lab"


class IsStaffMedical(BasePermission):
    """Tous les rôles professionnels (tout sauf patient)."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ("admin", "doctor", "nurse", "pharmacist", "lab")
        )


class IsDoctorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ("doctor", "admin")
        )


class IsDoctorOrNurseOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ("doctor", "nurse", "admin")
        )


class IsPharmacistOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ("pharmacist", "admin")
        )


class IsDoctorOrLabOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ("doctor", "lab", "admin")
        )


class IsLabOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ("lab", "admin")
        )


# Alias de compatibilité avec l'ancien nom
IsPharmacienOrAdmin = IsPharmacistOrAdmin


class IsOwnerOrMedicalStaff(BasePermission):
    """Patient accède à ses propres données ; staff médical accède à tout."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == "patient":
            return obj.patient.compte_patient == request.user
        return request.user.role in ("doctor", "nurse", "admin", "pharmacist", "lab")
