from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import User


class UserModelTest(TestCase):

    def test_creation_patient(self):
        user = User.objects.create_user(
            username='patient1',
            password='pass1234',
            role='patient'
        )
        self.assertEqual(user.role, 'patient')
        self.assertTrue(user.is_patient())
        self.assertFalse(user.is_doctor())

    def test_creation_medecin_avec_specialite(self):
        user = User(username='dr_diallo', role='doctor', specialite='Cardiologie')
        user.set_password('pass1234')
        user.full_clean()
        user.save()
        self.assertTrue(user.is_doctor())
        self.assertEqual(user.specialite, 'Cardiologie')

    def test_medecin_sans_specialite_invalide(self):
        user = User(username='dr_incomplet', role='doctor', specialite='')
        user.set_password('pass1234')
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_roles_helpers(self):
        roles = {
            'admin': 'admin1',
            'nurse': 'nurse1',
            'pharmacist': 'pharm1',
            'lab': 'lab1',
        }
        for role, username in roles.items():
            u = User.objects.create_user(username=username, password='p', role=role)
            self.assertTrue(getattr(u, f'is_{role}')())

    def test_is_active_status_par_defaut(self):
        user = User.objects.create_user(username='actif', password='p')
        self.assertTrue(user.is_active_status)

    def test_str_retourne_username(self):
        user = User.objects.create_user(username='testuser', password='p')
        self.assertEqual(str(user), 'testuser')
