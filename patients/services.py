from .models import Patient

def create_patient(data, user_creer):

    patient = Patient.objects.create(
        cree_par=user_creer,
        **data
    )

    return patient

def assign_medecin_traitant(patient, medecin):

    # sécurité métier
    if hasattr(medecin, "role") and medecin.role != "doctor":
        raise ValueError("Le compte doit être un médecin")

    patient.medecin_traitant = medecin
    patient.save()

    return patient

def link_compte_patient(patient, user):

    # sécurité métier
    if hasattr(user, "role") and user.role != "patient":
        raise ValueError("Le compte doit être un patient")

    patient.compte_patient = user
    patient.save()

    return patient
def update_patient(patient, **fields):

    for key, value in fields.items():
        setattr(patient, key, value)

    patient.save()

    return patient