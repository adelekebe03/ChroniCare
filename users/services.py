from core.utils import log_action
from .models import User


def register_user(user):
    log_action(
        user,
        "REGISTER",
        f"Utilisateur {user.username} inscrit",
        "User",
    )
    return user


def get_user_serializer_class(user, admin_serializer, public_serializer):
    if user.is_authenticated and (user.is_superuser or getattr(user, "role", None) == "admin"):
        return admin_serializer
    return public_serializer
