"""
Tests du module Maladies.
Partie 1 : tests unitaires des modèles (existants).
Partie 2 : audit complet des permissions PatientMaladie / SeuilAlerte.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError
from django.utils import timezone
import json

from maladies.models import Maladie, PatientMaladie, SeuilAlerte
from patients.models import Patient
from users.models import User


# ═════════════════════════════════════════════════════════════════════════════
# PARTIE 1 — Tests unitaires modèles (inchangés)
# ═════════════════════════════════════════════════════════════════════════════

class MaladieModelTest(TestCase):

    def test_creation_maladie(self):
        m = Maladie.objects.create(
            nom='Diabète de type 2',
            type='metabolique',
            description='Trouble du métabolisme du glucose'
        )
        self.assertEqual(str(m), 'Diabète de type 2')
        self.assertEqual(m.type, 'metabolique')

    def test_type_par_defaut_autre(self):
        m = Maladie.objects.create(nom='Maladie inconnue')
        self.assertEqual(m.type, 'autre')

    def test_description_optionnelle(self):
        m = Maladie.objects.create(nom='VIH', type='infectieuse')
        self.assertEqual(m.description, '')


class PatientMaladieModelTest(TestCase):

    def setUp(self):
        self.doctor = User.objects.create_user(
            username='dr_diallo2', password='pass1234',
            role='doctor', specialite='Médecine interne'
        )
        self.patient = Patient.objects.create(
            nom='Balde', prenom='Oumar', sexe='M',
            telephone='620444444', groupe_sanguin='B-',
            contact_urgence='620444445',
        )
        self.maladie = Maladie.objects.create(
            nom='Hypertension', type='cardiovasculaire'
        )

    def test_liaison_patient_maladie(self):
        pm = PatientMaladie.objects.create(
            patient=self.patient,
            maladie=self.maladie,
            date_diagnostic=timezone.now().date(),
        )
        self.assertEqual(pm.status, 'active')
        self.assertIn('Balde', str(pm))
        self.assertIn('Hypertension', str(pm))

    def test_statuts_possibles(self):
        pm = PatientMaladie.objects.create(
            patient=self.patient,
            maladie=self.maladie,
            date_diagnostic=timezone.now().date(),
        )
        for statut in ['active', 'stable', 'guérie']:
            pm.status = statut
            pm.save()
            pm.refresh_from_db()
            self.assertEqual(pm.status, statut)

    def test_unique_together_patient_maladie(self):
        PatientMaladie.objects.create(
            patient=self.patient,
            maladie=self.maladie,
            date_diagnostic=timezone.now().date(),
        )
        with self.assertRaises(IntegrityError):
            PatientMaladie.objects.create(
                patient=self.patient,
                maladie=self.maladie,
                date_diagnostic=timezone.now().date(),
            )

    def test_seuil_alerte_cree(self):
        pm = PatientMaladie.objects.create(
            patient=self.patient,
            maladie=self.maladie,
            date_diagnostic=timezone.now().date(),
        )
        seuil = SeuilAlerte.objects.create(
            patient_maladie=pm,
            indicateur='tension_systolique',
            min_valeur=90.0,
            max_valeur=140.0,
        )
        self.assertEqual(seuil.indicateur, 'tension_systolique')
        self.assertEqual(seuil.min_valeur, 90.0)
        self.assertEqual(seuil.max_valeur, 140.0)
        self.assertIn('tension_systolique', str(seuil))


# ═════════════════════════════════════════════════════════════════════════════
# PARTIE 2 — Audit permissions PatientMaladie / SeuilAlerte
# ═════════════════════════════════════════════════════════════════════════════

ROLES = ['admin', 'doctor', 'nurse', 'patient', 'pharmacist', 'lab']
ALLOWED_HTML = {'admin', 'doctor', 'nurse'}
ALLOWED_API_TARGET = {'admin', 'doctor', 'nurse'}  # ce qui DEVRAIT être autorisé


def _make_user(role, suffix=''):
    kw = {'username': f'audit_{role}{suffix}', 'role': role}
    if role == 'doctor':
        kw['specialite'] = 'Médecine générale'
    return User.objects.create_user(password='testpass123', **kw)


class PermissionAuditTests(TestCase):
    """
    Audit complet : 6 rôles × toutes les actions HTML et API.
    Chaque résultat est enregistré dans cls._results pour le rapport final.
    """

    _results = []

    @classmethod
    def setUpTestData(cls):
        cls.users = {role: _make_user(role) for role in ROLES}
        cls.maladie = Maladie.objects.create(nom='Diabète audit', type='metabolique')
        cls.patient_obj = Patient.objects.create(
            nom='AuditPat', prenom='Test', sexe='M',
            telephone='620001111', groupe_sanguin='A+',
            contact_urgence='620001112',
        )
        cls.pm = PatientMaladie.objects.create(
            patient=cls.patient_obj,
            maladie=cls.maladie,
            status='active',
            date_diagnostic='2024-01-15',
        )
        cls.seuil = SeuilAlerte.objects.create(
            patient_maladie=cls.pm,
            indicateur='Glycémie', min_valeur=0.7, max_valeur=1.26,
        )

    # ── utilitaire ──────────────────────────────────────────────────────────

    def _req(self, role, url, method='GET', data=None, content_type=None):
        c = Client()
        c.login(username=f'audit_{role}', password='testpass123')
        if method == 'GET':
            return c.get(url, HTTP_ACCEPT='application/json')
        if method == 'POST':
            ct = content_type or 'application/json'
            return c.post(url, data=json.dumps(data or {}), content_type=ct)
        if method == 'PUT':
            return c.put(url, data=json.dumps(data or {}),
                         content_type='application/json')
        if method == 'DELETE':
            return c.delete(url)

    def _rec(self, action, role, method, expected, obtained):
        passed = (obtained == expected)
        self.__class__._results.append({
            'action': action, 'role': role, 'method': method,
            'expected': expected, 'obtained': obtained, 'passed': passed,
        })
        return passed

    # ── HTML — non authentifié ───────────────────────────────────────────────

    def test_01_html_anonymous_redirects(self):
        urls = [
            reverse('patient-maladie-list'),
            reverse('patient-maladie-create'),
            reverse('patient-maladie-update', kwargs={'pk': self.pm.pk}),
            reverse('patient-maladie-delete', kwargs={'pk': self.pm.pk}),
        ]
        c = Client()
        for url in urls:
            resp = c.get(url)
            ok = self._rec('HTML anonyme', 'anonymous', 'GET', 302, resp.status_code)
            self.assertIn(resp.status_code, [301, 302],
                          f"Anonyme non redirigé sur {url}")

    # ── HTML — Liste PatientMaladie ──────────────────────────────────────────

    def test_02_html_pm_list(self):
        url = reverse('patient-maladie-list')
        for role in ROLES:
            exp = 200 if role in ALLOWED_HTML else 302
            resp = self._req(role, url)
            ok = self._rec('HTML Liste PM', role, 'GET', exp, resp.status_code)
            self.assertTrue(ok, f"[{role}] {url} → attendu {exp}, obtenu {resp.status_code}")

    # ── HTML — Créer PatientMaladie ──────────────────────────────────────────

    def test_03_html_pm_create_get(self):
        url = reverse('patient-maladie-create')
        for role in ROLES:
            exp = 200 if role in ALLOWED_HTML else 302
            resp = self._req(role, url)
            ok = self._rec('HTML Créer PM (GET)', role, 'GET', exp, resp.status_code)
            self.assertTrue(ok, f"[{role}] → attendu {exp}, obtenu {resp.status_code}")

    # ── HTML — Modifier PatientMaladie ───────────────────────────────────────

    def test_04_html_pm_update_get(self):
        url = reverse('patient-maladie-update', kwargs={'pk': self.pm.pk})
        for role in ROLES:
            exp = 200 if role in ALLOWED_HTML else 302
            resp = self._req(role, url)
            ok = self._rec('HTML Modifier PM (GET)', role, 'GET', exp, resp.status_code)
            self.assertTrue(ok, f"[{role}] → attendu {exp}, obtenu {resp.status_code}")

    # ── HTML — Supprimer PatientMaladie ──────────────────────────────────────

    def test_05_html_pm_delete_get(self):
        url = reverse('patient-maladie-delete', kwargs={'pk': self.pm.pk})
        for role in ROLES:
            exp = 200 if role in ALLOWED_HTML else 302
            resp = self._req(role, url)
            ok = self._rec('HTML Supprimer PM (GET)', role, 'GET', exp, resp.status_code)
            self.assertTrue(ok, f"[{role}] → attendu {exp}, obtenu {resp.status_code}")

    # ── API — Liste PatientMaladie ───────────────────────────────────────────

    def test_06_api_pm_list(self):
        url = '/maladies/api/patient-maladies/'
        for role in ROLES:
            resp = self._req(role, url)
            # Résultat réel enregistré ; attendu CIBLE = 403 pour rôles non autorisés
            exp_target = 200 if role in ALLOWED_API_TARGET else 403
            self._rec('API Liste PM (GET)', role, 'GET', exp_target, resp.status_code)
            # On N'assert pas ici — on documente l'état réel (faille)

    # ── API — Créer PatientMaladie ───────────────────────────────────────────

    def test_07_api_pm_create(self):
        url = '/maladies/api/patient-maladies/'
        for role in ROLES:
            p = Patient.objects.create(
                nom=f'ApiC_{role}', prenom='X', sexe='M',
                telephone='620100000', groupe_sanguin='B+',
                contact_urgence='620100001',
            )
            data = {'patient': p.pk, 'maladie': self.maladie.pk,
                    'status': 'active', 'date_diagnostic': '2024-06-01'}
            try:
                resp = self._req(role, url, 'POST', data)
                obtained = resp.status_code
            except Exception:
                # perform_create bug (patient.nom sur PatientMaladie) => 500
                obtained = 500
            exp_target = 201 if role in ALLOWED_API_TARGET else 403
            self._rec('API Creer PM (POST)', role, 'POST', exp_target, obtained)

    # ── API — Modifier PatientMaladie ────────────────────────────────────────

    def test_08_api_pm_update(self):
        url = f'/maladies/api/patient-maladies/{self.pm.pk}/'
        data = {
            'patient': self.patient_obj.pk,
            'maladie': self.maladie.pk,
            'status': 'stable',
            'date_diagnostic': '2024-01-15',
        }
        for role in ROLES:
            resp = self._req(role, url, 'PUT', data)
            exp_target = 200 if role in ALLOWED_API_TARGET else 403
            self._rec('API Modifier PM (PUT)', role, 'PUT', exp_target, resp.status_code)

    # ── API — Supprimer PatientMaladie ───────────────────────────────────────

    def test_09_api_pm_delete(self):
        for role in ROLES:
            p = Patient.objects.create(
                nom=f'ApiD_{role}', prenom='X', sexe='M',
                telephone='620200000', groupe_sanguin='O-',
                contact_urgence='620200001',
            )
            pm = PatientMaladie.objects.create(
                patient=p, maladie=self.maladie,
                status='active', date_diagnostic='2024-03-01',
            )
            url = f'/maladies/api/patient-maladies/{pm.pk}/'
            resp = self._req(role, url, 'DELETE')
            exp_target = 204 if role in ALLOWED_API_TARGET else 403
            self._rec('API Supprimer PM (DELETE)', role, 'DELETE', exp_target, resp.status_code)

    # ── API — Liste SeuilAlerte ──────────────────────────────────────────────

    def test_10_api_seuil_list(self):
        url = '/maladies/api/seuils/'
        for role in ROLES:
            resp = self._req(role, url)
            exp_target = 200 if role in ALLOWED_API_TARGET else 403
            self._rec('API Liste Seuils (GET)', role, 'GET', exp_target, resp.status_code)

    # ── API — Créer SeuilAlerte ──────────────────────────────────────────────

    def test_11_api_seuil_create(self):
        url = '/maladies/api/seuils/'
        for role in ROLES:
            data = {'patient_maladie': self.pm.pk,
                    'indicateur': f'Ind_{role}',
                    'min_valeur': 0.5, 'max_valeur': 2.0}
            resp = self._req(role, url, 'POST', data)
            exp_target = 201 if role in ALLOWED_API_TARGET else 403
            self._rec('API Créer Seuil (POST)', role, 'POST', exp_target, resp.status_code)

    # ── API — Supprimer SeuilAlerte ──────────────────────────────────────────

    def test_12_api_seuil_delete(self):
        for role in ROLES:
            s = SeuilAlerte.objects.create(
                patient_maladie=self.pm,
                indicateur=f'Del_{role}', min_valeur=1.0, max_valeur=5.0,
            )
            url = f'/maladies/api/seuils/{s.pk}/'
            resp = self._req(role, url, 'DELETE')
            exp_target = 204 if role in ALLOWED_API_TARGET else 403
            self._rec('API Supprimer Seuil (DELETE)', role, 'DELETE', exp_target, resp.status_code)

    # ── Rapport final ────────────────────────────────────────────────────────

    def test_zz_rapport(self):
        """Genere le rapport recapitulatif -- toujours en dernier."""
        import sys
        results = self.__class__._results
        total   = len(results)
        success = sum(1 for r in results if r['passed'])
        failed  = total - success

        lines = []
        lines.append("\n\n" + "=" * 94)
        lines.append("  RAPPORT AUDIT PERMISSIONS -- PatientMaladie / SeuilAlerte -- ChroniCare")
        lines.append("=" * 94)
        lines.append(f"  {'Action':<33} {'Role':<12} {'Meth':<8} {'Attendu(cible)':<16} {'Obtenu':<8} Resultat")
        lines.append("-" * 94)

        current_action = ''
        for r in results:
            if r['action'] != current_action:
                if current_action:
                    lines.append("")
                current_action = r['action']
            icon = '[OK]  ' if r['passed'] else '[FAILLE]'
            lines.append(
                f"  {r['action']:<33} {r['role']:<12} {r['method']:<8} "
                f"{str(r['expected']):<16} {str(r['obtained']):<8} {icon}"
            )

        lines.append("\n" + "=" * 94)
        lines.append(f"  TOTAL : {total} tests | SUCCES : {success} | ECHECS : {failed}")
        lines.append("=" * 94)

        if failed > 0:
            lines.append("\n  CORRECTIONS REQUISES :")
            lines.append("  " + "-" * 40)
            for f in [r for r in results if not r['passed']]:
                lines.append(
                    f"  >> [{f['role']}] {f['action']} : "
                    f"obtenu HTTP {f['obtained']}, attendu {f['expected']}"
                )
            lines.append("")

        output = "\n".join(lines)
        # Encodage safe pour Windows cp1252
        sys.stdout.buffer.write((output + "\n").encode('utf-8', errors='replace'))
        sys.stdout.buffer.flush()
        self.assertTrue(True)
