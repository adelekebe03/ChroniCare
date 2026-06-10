from django.test import TestCase
from patients.models import Patient
from users.models import User


class PatientModelTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='dr_camara',
            password='pass1234',
            role='doctor',
            specialite='Médecine générale'
        )

    def _make_patient(self, nom='Diallo', prenom='Mamadou', **kwargs):
        defaults = dict(
            nom=nom,
            prenom=prenom,
            sexe='M',
            telephone='620000001',
            groupe_sanguin='O+',
            contact_urgence='620000002',
        )
        defaults.update(kwargs)
        return Patient.objects.create(**defaults)

    def test_creation_patient(self):
        patient = self._make_patient(medecin_traitant=self.doctor, cree_par=self.doctor)
        self.assertEqual(str(patient), 'Diallo Mamadou')
        self.assertEqual(patient.medecin_traitant, self.doctor)

    def test_nom_complet(self):
        patient = self._make_patient(nom='Bah', prenom='Fatoumata', sexe='F',
                                     telephone='620000003', groupe_sanguin='A+',
                                     contact_urgence='620000004')
        self.assertEqual(patient.nom_complet, 'Fatoumata Bah')

    def test_patient_sans_medecin(self):
        patient = self._make_patient(nom='Sylla', prenom='Ibrahim',
                                     telephone='620000005', groupe_sanguin='B+',
                                     contact_urgence='620000006')
        self.assertIsNone(patient.medecin_traitant)

    def test_groupe_sanguin_valide(self):
        for groupe in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            p = Patient.objects.create(
                nom='Test', prenom='GS', sexe='M',
                telephone='0000', groupe_sanguin=groupe, contact_urgence='0000'
            )
            self.assertEqual(p.groupe_sanguin, groupe)

    def test_ordering_par_date_creation(self):
        p1 = self._make_patient(nom='Alpha', prenom='A', telephone='1', contact_urgence='1')
        p2 = self._make_patient(nom='Beta', prenom='B', telephone='2', contact_urgence='2')
        patients = list(Patient.objects.all())
        self.assertEqual(patients[0], p2)
        self.assertEqual(patients[1], p1)
