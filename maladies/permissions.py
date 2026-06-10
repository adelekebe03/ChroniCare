# Toutes les permissions sont centralisées dans users.permissions.
# Ce fichier conserve des alias pour la compatibilité avec du code existant.
from users.permissions import IsStaffMedical, IsOwnerOrMedicalStaff  # noqa: F401

IsMedicalStaff = IsStaffMedical
IsOwnerOrDoctor = IsOwnerOrMedicalStaff
