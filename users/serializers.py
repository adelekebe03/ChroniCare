from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Inscription publique : le rôle est forcé à 'patient'.
    La création d'autres rôles (doctor, admin…) est réservée à l'admin
    via l'interface HTML /users/register/.
    """
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role='patient',
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'photo',
            'specialite',
            'contact',
            'signature',
            'is_active_status',
        ]


class UserPublicSerializer(serializers.ModelSerializer):
    """Données visibles par les non-admins (ex: liste des médecins)."""
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'role',
            'photo',
            'specialite',
            'contact',
        ]


class UserAdminSerializer(serializers.ModelSerializer):
    """Données complètes, réservées à l'admin."""
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'is_active_status',
            'is_staff',
            'is_superuser',
            'specialite',
            'contact',
            'created_at',
            'updated_at',
        ]
