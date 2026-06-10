from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

from . import views
from .views import UserViewSet, RegisterView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    # ============================================================
    # AUTH HTML — connexion / inscription / déconnexion
    # ============================================================
    path('user/login/',    views.user_login,       name='user-login'),
    path('user/logout/',   views.user_logout,      name='user-logout'),

    # ============================================================
    # PASSWORD RESET (vues Django built-in + templates personnalisés)
    # ============================================================
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),

    # ============================================================
    # PROFILE
    # ============================================================
    path('profile/',      views.profile,       name='profile'),
    path('profile/edit/', views.profile_edit,  name='profile-edit'),

    # ============================================================
    # ADMIN — gestion des utilisateurs
    # ============================================================
    path('list/',                   views.user_list,     name='user-list'),
    path('register/',               views.user_register,           name='user-register'),
    path('register/patient/',       views.register_patient_account, name='register-patient-account'),
    path('<int:pk>/detail/',        views.user_detail,   name='user-detail'),
    path('<int:user_id>/edit/',     views.user_edit,     name='user-edit'),
    path('<int:user_id>/delete/',   views.user_delete,   name='user-delete'),

    # ============================================================
    # API
    # ============================================================
    path('api/',          include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),
]
