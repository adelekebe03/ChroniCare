from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, time
from unittest.mock import patch

from appointments.models import Appointment
from patients.models import Patient
from users.models import User


class AppointmentModelTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='dr_keita', password='pass1234',
            role='doctor', specialite='Pédiatrie'
        )
        self.patient = Patient.objects.create(
            nom='Conde', prenom='Alpha', sexe='M',
            telephone='620111111', groupe_sanguin='AB+',
            contact_urgence='620111112',
        )
        self.future_date = (timezone.now() + timedelta(days=30)).date()
        self.heure = time(9, 0)

    def _make_rdv(self, patient=None, doctor=None, date=None, heure=None, **kwargs):
        return Appointment.objects.create(
            patient=patient or self.patient,
            doctor=doctor or self.doctor,
            date=date or self.future_date,
            heure=heure or self.heure,
            **kwargs
        )

    def test_creation_rendez_vous(self):
        rdv = self._make_rdv(motif='Consultation')
        self.assertEqual(rdv.status, 'planifie')
        self.assertFalse(rdv.is_reminded)
        self.assertEqual(rdv.motif, 'Consultation')

    def test_str_contient_patient(self):
        rdv = self._make_rdv()
        self.assertIn('Conde', str(rdv))

    def test_conflit_medecin_meme_heure(self):
        self._make_rdv()
        patient2 = Patient.objects.create(
            nom='Toure', prenom='Sekou', sexe='M',
            telephone='620222222', groupe_sanguin='O-',
            contact_urgence='620222223',
        )
        with self.assertRaises(ValidationError):
            self._make_rdv(patient=patient2)

    def test_conflit_patient_meme_heure(self):
        doctor2 = User.objects.create_user(
            username='dr_barry', password='pass1234',
            role='doctor', specialite='Chirurgie'
        )
        self._make_rdv()
        with self.assertRaises(ValidationError):
            self._make_rdv(doctor=doctor2)

    def test_rdv_date_passee_invalide(self):
        past_date = (timezone.now() - timedelta(days=1)).date()
        with self.assertRaises(ValidationError):
            self._make_rdv(date=past_date)

    def test_statuts_valides(self):
        rdv = self._make_rdv()
        for statut in ['planifie', 'effectue', 'annule']:
            rdv.status = statut
            rdv.save()
            rdv.refresh_from_db()
            self.assertEqual(rdv.status, statut)

    def test_deux_rdv_meme_medecin_heures_differentes(self):
        self._make_rdv(heure=time(9, 0))
        rdv2 = self._make_rdv(heure=time(10, 0))
        self.assertIsNotNone(rdv2.pk)
