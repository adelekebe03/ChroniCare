"""
Migration 0014 — Refactoring pharmacie maladies chroniques :

1. Dispensation.prescription : OneToOneField → ForeignKey (PROTECT)
   Permet N dispensations (renouvellements) par prescription.

2. Dispensation.periode : nouveau champ DateField
   Identifie le mois de dispensation — contrainte d'unicité (prescription, periode).

3. MouvementStock : nouveau modèle d'audit des entrées/sorties de stock.

4. Prescription.maladie : nouveau FK optionnel vers Maladie.

5. MedicationLot.date_reception : nouveau champ DateField.

6. PrescriptionItem.frequence : CharField libre → CharField avec choices.

7. Prescription.statut : ajout état 'active' et 'terminee'.
"""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacie', '0013_fix_dispensation_pharmacist_role'),
        ('maladies',  '0002_initial'),
        ('suivi_medical', '0009_add_biological_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        # ── 1. Dispensation.prescription : OneToOneField → ForeignKey ──────
        migrations.AlterField(
            model_name='dispensation',
            name='prescription',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='dispensations',
                to='pharmacie.prescription',
                verbose_name='Prescription',
            ),
        ),

        # ── 2. Dispensation.periode ─────────────────────────────────────────
        migrations.AddField(
            model_name='dispensation',
            name='periode',
            field=models.DateField(
                null=True, blank=True,
                verbose_name='Période (mois)',
            ),
        ),

        # ── 3. Contrainte d'unicité (prescription, periode) ─────────────────
        migrations.AddConstraint(
            model_name='dispensation',
            constraint=models.UniqueConstraint(
                fields=['prescription', 'periode'],
                name='unique_dispensation_par_periode',
            ),
        ),

        # ── 4. MedicationLot.date_reception ────────────────────────────────
        migrations.AddField(
            model_name='medicationlot',
            name='date_reception',
            field=models.DateField(
                default=django.utils.timezone.now,
                verbose_name='Date de réception',
            ),
        ),

        # ── 5. Prescription.maladie ─────────────────────────────────────────
        migrations.AddField(
            model_name='prescription',
            name='maladie',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='prescriptions',
                to='maladies.maladie',
                verbose_name='Maladie chronique concernée',
            ),
        ),

        # ── 6. Prescription.statut : ajout 'active' et 'terminee' ──────────
        migrations.AlterField(
            model_name='prescription',
            name='statut',
            field=models.CharField(
                choices=[
                    ('en_attente', 'En attente'),
                    ('active',     'Active'),
                    ('terminee',   'Terminée'),
                    ('annulee',    'Annulée'),
                ],
                default='en_attente',
                max_length=20,
                verbose_name='Statut',
            ),
        ),

        # ── 7. PrescriptionItem.frequence → choices ─────────────────────────
        migrations.AlterField(
            model_name='prescriptionitem',
            name='frequence',
            field=models.CharField(
                choices=[
                    ('1_par_jour',    '1 fois par jour'),
                    ('2_par_jour',    '2 fois par jour'),
                    ('3_par_jour',    '3 fois par jour'),
                    ('1_par_semaine', '1 fois par semaine'),
                    ('au_besoin',     'Au besoin'),
                ],
                default='1_par_jour',
                max_length=30,
                verbose_name='Fréquence',
            ),
        ),

        # ── 8. MouvementStock ───────────────────────────────────────────────
        migrations.CreateModel(
            name='MouvementStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_mouvement', models.CharField(
                    choices=[
                        ('reception',    'Réception'),
                        ('dispensation', 'Dispensation'),
                        ('peremption',   'Péremption / ajustement'),
                    ],
                    max_length=20,
                    verbose_name='Type',
                )),
                ('quantite', models.IntegerField(verbose_name='Quantité (+ entrée / − sortie)')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('reference', models.CharField(blank=True, max_length=200, verbose_name='Référence')),
                ('dispensation', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='mouvements',
                    to='pharmacie.dispensation',
                    verbose_name='Dispensation liée',
                )),
                ('lot', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='mouvements',
                    to='pharmacie.medicationlot',
                    verbose_name='Lot',
                )),
                ('utilisateur', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='mouvements_stock',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Utilisateur',
                )),
            ],
            options={
                'verbose_name': 'Mouvement de stock',
                'verbose_name_plural': 'Mouvements de stock',
                'ordering': ['-date'],
            },
        ),
    ]
