"""
Migration 0010 — Application des règles métier ChroniCare :
- suivi        : nullable → NOT NULL + PROTECT
- prescripteur : nullable → NOT NULL + PROTECT
- prescription : suppression du FK pharmacie (couplage incorrect)
- valeur_secondaire : nouveau champ (diastolique pour tension artérielle)
Base vide : aucune donnée à migrer.
"""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratoire', '0009_alter_labtest_date_test_alter_labtest_maladie_and_more'),
        ('suivi_medical', '0008_suivimedical_type_suivi'),
        ('pharmacie', '0013_fix_dispensation_pharmacist_role'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        # 1. suivi : SET_NULL nullable → PROTECT NOT NULL
        migrations.AlterField(
            model_name='labtest',
            name='suivi',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='analyses',
                to='suivi_medical.suivimedical',
                verbose_name='Suivi médical lié',
            ),
        ),

        # 2. prescripteur : nullable → NOT NULL + PROTECT
        migrations.AlterField(
            model_name='labtest',
            name='prescripteur',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='analyses_prescrites',
                limit_choices_to={'role': 'doctor'},
                to=settings.AUTH_USER_MODEL,
                verbose_name='Médecin prescripteur',
            ),
        ),

        # 3. Suppression du FK prescription (circuit pharmacie ≠ circuit labo)
        migrations.RemoveField(
            model_name='labtest',
            name='prescription',
        ),

        # 4. Ajout de valeur_secondaire (diastolique pour tension artérielle)
        migrations.AddField(
            model_name='labtest',
            name='valeur_secondaire',
            field=models.FloatField(
                null=True,
                blank=True,
                verbose_name='Valeur secondaire (ex : diastolique)',
            ),
        ),
    ]
