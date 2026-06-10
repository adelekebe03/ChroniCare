from .models import Maladie, PatientMaladie


# =========================
# 1. ASSIGNER UNE MALADIE
# =========================
def assign_maladie_to_patient(patient, maladie, status="active", observations=""):

    obj, created = PatientMaladie.objects.get_or_create(
        patient=patient,
        maladie=maladie,
        defaults={
            "status": status,
            "observations": observations
        }
    )

    if not created:
        obj.status = status
        obj.observations = observations
        obj.save()

    return obj


# =========================
# 2. UPDATE STATUS
# =========================
def update_patient_maladie_status(patient_maladie, status):

    patient_maladie.status = status
    patient_maladie.save()

    return patient_maladie


# =========================
# 3. DETECTION DEPUIS LAB TEST
# =========================
def detect_maladie_from_labtest(labtest):

    type_test = labtest.type_test.lower()
    maladie = None

    # GLYCÉMIE → DIABÈTE
    if type_test == "glycémie":
        if labtest.valeur and labtest.valeur > 1.26:
            maladie = Maladie.objects.filter(nom__icontains="diab").first()

    # CD4 → VIH
    elif type_test == "cd4":
        if labtest.valeur and labtest.valeur < 200:
            maladie = Maladie.objects.filter(nom__icontains="vih").first()

    # TENSION → HYPERTENSION
    elif type_test == "tension":
        if labtest.valeur and labtest.valeur > 14:
            maladie = Maladie.objects.filter(nom__icontains="hyper").first()

    # ASSIGNATION AUTOMATIQUE
    if maladie:
        return assign_maladie_to_patient(
            labtest.patient,
            maladie,
            status="active",
            observations=f"Détecté via {labtest.type_test}"
        )

    return None


# =========================
# 4. RESUME PATIENT
# =========================
def get_patient_maladie_summary(patient):

    maladies = patient.maladies.all()

    return {
        "total": maladies.count(),
        "actives": maladies.filter(status="active").count(),
        "stables": maladies.filter(status="stable").count(),
        "gueries": maladies.filter(status="guérie").count(),
    }
def process_lab_workflow(labtest):

    detect_maladie_from_labtest(labtest)

    return labtest