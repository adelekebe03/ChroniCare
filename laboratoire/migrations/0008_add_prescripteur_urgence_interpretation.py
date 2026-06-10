from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('laboratoire', '0007_alter_labtest_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Nouveau champ : médecin prescripteur ──────────────────────
        migrations.AddField(
            model_name='labtest',
            name='prescripteur',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='analyses_prescrites',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Médecin prescripteur',
                limit_choices_to={'role': 'doctor'},
            ),
        ),
        # ── Nouveau champ : analyse urgente ──────────────────────────
        migrations.AddField(
            model_name='labtest',
            name='urgence',
            field=models.BooleanField(default=False, verbose_name='Analyse urgente'),
        ),
        # ── Nouveaux champs : lecture médecin ────────────────────────
        migrations.AddField(
            model_name='labtest',
            name='lu_par_medecin',
            field=models.BooleanField(default=False, verbose_name='Lu par le médecin'),
        ),
        migrations.AddField(
            model_name='labtest',
            name='date_lecture',
            field=models.DateTimeField(
                blank=True, null=True,
                verbose_name='Date de lecture',
            ),
        ),
        migrations.AddField(
            model_name='labtest',
            name='notes_medecin',
            field=models.TextField(
                blank=True, null=True,
                verbose_name='Interprétation médecin',
            ),
        ),
        # ── Modification : type_test → choices standardisés ──────────
        migrations.AlterField(
            model_name='labtest',
            name='type_test',
            field=models.CharField(
                choices=[
                    ('glycemie',      'Glycémie'),
                    ('cd4',           'CD4'),
                    ('charge_virale', 'Charge virale'),
                    ('nfs',           'NFS / Hémogramme'),
                    ('creatinine',    'Créatinine'),
                    ('uree',          'Urée sanguine'),
                    ('transaminases', 'Transaminases (ALAT/ASAT)'),
                    ('hemoglobine',   'Hémoglobine'),
                    ('cholesterol',   'Cholestérol'),
                    ('tension',       'Tension artérielle'),
                    ('autre',         'Autre'),
                ],
                max_length=30,
                verbose_name="Type d'analyse",
            ),
        ),
        # ── Mise à jour Meta ─────────────────────────────────────────
        migrations.AlterModelOptions(
            name='labtest',
            options={
                'ordering': ['-date_test'],
                'verbose_name': 'Analyse de laboratoire',
                'verbose_name_plural': 'Analyses de laboratoire',
            },
        ),
    ]
