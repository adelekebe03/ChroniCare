from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from rest_framework import viewsets

from core.utils import log_action
from .models import Patient
from .serializers import PatientSerializer
from .forms import PatientForm
from suivi_medical.models import SuiviMedical
from users.permissions import IsDoctorOrNurseOrAdmin, IsDoctorOrAdmin
from users.decorators import role_required


# ============================================================
# API
# ============================================================

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_permissions(self):
        # Lecture : doctor, nurse, admin
        # Écriture (create/update/delete) : doctor et admin uniquement
        if self.action in ('list', 'retrieve'):
            return [IsDoctorOrNurseOrAdmin()]
        return [IsDoctorOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Patient.objects.none()

        qs = Patient.objects.select_related('compte_patient', 'medecin_traitant')
        role = getattr(user, "role", None)

        if role == 'patient':
            return qs.filter(compte_patient=user)
        if role == 'doctor':
            return qs.filter(medecin_traitant=user)
        return qs

    def perform_create(self, serializer):
        patient = serializer.save(cree_par=self.request.user)
        log_action(
            self.request.user,
            "CREATE_PATIENT",
            f"Patient {patient.nom} créé",
            "PATIENT",
        )


# ============================================================
# HTML
# ============================================================

@role_required("admin", "doctor", "nurse")
def patient_list(request):
    patients = Patient.objects.select_related('medecin_traitant', 'compte_patient').prefetch_related('maladies').all()

    nom = request.GET.get('nom')
    sexe = request.GET.get('sexe')
    groupe = request.GET.get('groupe')

    if nom:
        patients = patients.filter(Q(nom__icontains=nom) | Q(prenom__icontains=nom))
    if sexe:
        patients = patients.filter(sexe=sexe)
    if groupe:
        patients = patients.filter(groupe_sanguin=groupe)

    return render(request, "patients/patient_list.html", {
        "patients": patients,
        "page_title": "Gestion des patients",
    })


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    role = getattr(request.user, 'role', None)
    if role == 'patient' and patient.compte_patient != request.user:
        messages.error(request, "Accès non autorisé à ce dossier patient.")
        return redirect('dashboard')
    suivis = SuiviMedical.objects.filter(patient=patient).order_by('-created_at')[:5]
    return render(request, "patients/patient_detail.html", {
        "patient": patient,
        "suivis": suivis,
        "page_title": f"{patient.nom} {patient.prenom}",
    })


@role_required("admin", "doctor", "nurse")
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.cree_par = request.user
            patient.save()

            user = patient.compte_patient
            if user:
                user.role = "patient"
                user.is_active = True
                user.save()

            messages.success(request, "Patient enregistré avec succès.")
            return redirect('patient-list')
    else:
        form = PatientForm()
    return render(request, 'patients/patient_form.html', {
        'form': form,
        'page_title': "Nouveau patient",
    })


@role_required("admin", "doctor", "nurse")
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            user = patient.compte_patient
            if user:
                user.role = "patient"
                user.save()
            log_action(request.user, "UPDATE_PATIENT", f"Patient {patient.nom} mis à jour", "PATIENT")
            messages.success(request, "Patient mis à jour.")
            return redirect('patient-list')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {
        'form': form,
        'page_title': f"Modifier : {patient.nom} {patient.prenom}",
    })


@role_required("admin", "doctor", "nurse")
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        log_action(request.user, "DELETE_PATIENT", f"Patient {patient.nom} {patient.prenom} supprimé", "PATIENT")
        patient.delete()
        messages.success(request, "Patient supprimé.")
        return redirect('patient-list')
    return render(request, 'patients/patient_confirm_delete.html', {
        'patient': patient,
        'page_title': f"Supprimer {patient.nom} {patient.prenom}",
    })


@login_required
def dossier_medical(request, pk):
    patient = get_object_or_404(Patient, id=pk)
    role = getattr(request.user, 'role', None)
    if role == 'patient' and patient.compte_patient != request.user:
        messages.error(request, "Accès non autorisé à ce dossier médical.")
        return redirect('dashboard')
    suivis = SuiviMedical.objects.filter(patient=patient).order_by('-created_at')
    return render(request, 'patients/dossier_medical.html', {
        'patient': patient,
        'suivis': suivis,
        'page_title': f"Dossier — {patient.nom} {patient.prenom}",
    })
