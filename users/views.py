from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny  # noqa: F401 (conservé si besoin futur)

from .models import User
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserAdminSerializer,
    UserPublicSerializer,
)
from .services import register_user, get_user_serializer_class
from .forms import UserForm, UserRegisterForm, UserProfileForm, PatientAccountRegisterForm
from .permissions import IsAdmin
from .decorators import admin_required, role_required


# ============================================================
# API
# ============================================================

class RegisterView(generics.CreateAPIView):
    """
    Inscription publique — rôle forcé à 'patient' par le serializer.
    La création de comptes admin/doctor/nurse/etc. passe par /users/register/ (HTML, admin uniquement).
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        user = serializer.save()
        register_user(user)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD utilisateurs via API — réservé à l'administrateur."""
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        return get_user_serializer_class(
            self.request.user,
            UserAdminSerializer,
            UserPublicSerializer,
        )


# ============================================================
# UTIL : redirection après login selon rôle
# ============================================================
ROLE_DASHBOARD_URLS = {
    "admin":      "admin-dashboard",
    "doctor":     "medecin-dashboard",
    "nurse":      "infirmier-dashboard",
    "patient":    "patient-dashboard",
    "pharmacist": "pharmacien-dashboard",
    "lab":        "laboratoire-dashboard",
}


def _redirect_to_dashboard(user):
    role = getattr(user, "role", None)
    return ROLE_DASHBOARD_URLS.get(role, "dashboard")


# ============================================================
# AUTH HTML
# ============================================================

def user_login(request):
    if request.user.is_authenticated:
        return redirect(_redirect_to_dashboard(request.user))

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        remember = request.POST.get("remember_me")

        # Résolution insensible à la casse : "moriba08" → "Moriba08"
        raw_user = None
        try:
            raw_user = User.objects.get(username__iexact=username)
            username = raw_user.username
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            raw_user = None

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active_status:
                # Compte suspendu manuellement (is_active_status=False)
                messages.error(
                    request,
                    "Ce compte a été suspendu. Contactez votre administrateur."
                )
            else:
                login(request, user)
                if not remember:
                    request.session.set_expiry(0)
                messages.success(
                    request,
                    f"Bienvenue {user.get_full_name() or user.username} !"
                )
                return redirect(_redirect_to_dashboard(user))

        elif raw_user is not None and not raw_user.is_active and raw_user.check_password(password):
            # Compte Django désactivé (is_active=False) — password correct
            messages.error(
                request,
                "Ce compte a été désactivé. Contactez votre administrateur."
            )
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, "registration/login.html")


@login_required
def user_logout(request):
    if request.method == "POST":
        username = request.user.get_full_name() or request.user.username
        logout(request)
        messages.success(request, f"À bientôt {username} !")
        return redirect("user-login")
    return render(request, "registration/logout_confirm.html")


# ============================================================
# PROFILE
# ============================================================

@login_required
def profile(request):
    return render(request, "users/profile.html", {"user_obj": request.user})


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "users/profile_edit.html", {"form": form})


# ============================================================
# ADMIN : CRUD utilisateurs (réservé admin)
# ============================================================

@admin_required
def user_list(request):
    users = User.objects.all().order_by("-date_joined")
    context = {
        "users":       users,
        "total_users": users.count(),
        "doctors":     users.filter(role="doctor").count(),
        "patients":    users.filter(role="patient").count(),
        "nurses":      users.filter(role="nurse").count(),
        "pharmacists": users.filter(role="pharmacist").count(),
        "labs":        users.filter(role="lab").count(),
    }
    return render(request, "users/user_list.html", context)


@login_required
def user_detail(request, pk):
    if not request.user.role == "admin" and request.user.pk != pk:
        messages.error(request, "Accès non autorisé.")
        return redirect("dashboard")
    user_obj = get_object_or_404(User, id=pk)
    return render(request, "users/user_detail.html", {"user_obj": user_obj})


@admin_required
def user_register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Utilisateur créé avec succès.")
            return redirect("user-list")
    else:
        form = UserRegisterForm()
    return render(request, "users/user_register.html", {"form": form})


@admin_required
def user_edit(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur mis à jour.")
            return redirect("user-list")
    else:
        form = UserForm(instance=user_obj)
    return render(request, "users/user_edit.html", {"form": form, "user_obj": user_obj})


@admin_required
def user_delete(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user_obj.delete()
        messages.success(request, "Utilisateur supprimé.")
        return redirect("user-list")
    return render(request, "users/user_confirm_delete.html", {"user_obj": user_obj})


# ============================================================
# MÉDECIN : créer un compte utilisateur pour un patient
# ============================================================

@role_required("doctor", "admin")
def register_patient_account(request):
    """
    Seuls les médecins (et l'admin) peuvent créer des comptes utilisateurs patients.
    Après création, redirige vers la création du dossier patient pour lier les deux.
    """
    if request.method == "POST":
        form = PatientAccountRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "patient"
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(
                request,
                f"Compte patient créé pour {user.get_full_name() or user.username}. "
                "Complétez maintenant le dossier médical ci-dessous."
            )
            return redirect("patient-create")
    else:
        form = PatientAccountRegisterForm()
    return render(request, "users/register_patient_account.html", {"form": form})
