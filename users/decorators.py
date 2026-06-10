from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*allowed_roles):
    """Décorateur pour les vues HTML : vérifie le rôle de l'utilisateur connecté."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("user-login")
            if getattr(request.user, "role", None) not in allowed_roles:
                messages.error(request, "Accès non autorisé pour votre rôle.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def admin_required(view_func):
    """Raccourci : réservé aux administrateurs."""
    return role_required("admin")(view_func)
