from django.test import TestCase
from suivi_medical.models import SuiviMedical
from patients.models import Patient
from users.models import User


class SuiviMedicalModelTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='dr_soumah', password='pass1234',
            role='doctor', specialite='Endocrinologie'
        )
        self.patient = Patient.objects.create(
            nom='Camara', prenom='Kadiatou', sexe='F',
            telephone='620333333', groupe_sanguin='A-',
            contact_urgence='620333334',
        )

    def _make_suivi(self, **kwargs):
        return SuiviMedical.objects.create(
            patient=self.patient, medecin=self.doctor, **kwargs
        )

    def test_calcul_imc_correct(self):
        suivi = self._make_suivi(poids=70, taille=175)
        imc_attendu = round(70 / (1.75 ** 2), 2)
        self.assertEqual(suivi.imc, imc_attendu)

    def test_imc_sans_poids_est_none(self):
        suivi = self._make_suivi(taille=175)
        self.assertIsNone(suivi.imc)

    def test_imc_sans_taille_est_none(self):
        suivi = self._make_suivi(poids=70)
        self.assertIsNone(suivi.imc)

    def test_imc_taille_zero_est_none(self):
        suivi = self._make_suivi(poids=70, taille=0)
        self.assertIsNone(suivi.imc)

    def test_statut_par_defaut_stable(self):
        suivi = self._make_suivi()
        self.assertEqual(suivi.statut, 'stable')

    def test_statut_critique(self):
        suivi = self._make_suivi(glycemie=3.5, statut='critique')
        self.assertEqual(suivi.statut, 'critique')

    def test_donnees_vitales_enregistrees(self):
        suivi = self._make_suivi(
            tension_systolique=140,
            tension_diastolique=90,
            glycemie=1.3,
            cd4=350,
            charge_virale=1000,
        )
        self.assertEqual(suivi.tension_systolique, 140)
        self.assertEqual(suivi.tension_diastolique, 90)
        self.assertAlmostEqual(suivi.glycemie, 1.3)

    def test_type_suivi_par_defaut_rdv(self):
        suivi = self._make_suivi()
        self.assertEqual(suivi.type_suivi, 'rdv')

    def test_ordering_desc_created_at(self):
        s1 = self._make_suivi(observations='premier')
        s2 = self._make_suivi(observations='deuxieme')
        suivis = list(SuiviMedical.objects.all())
        self.assertEqual(suivis[0], s2)
        self.assertEqual(suivis[1], s1)
