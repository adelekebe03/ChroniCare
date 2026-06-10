"""
Migration 0009 — Ajout des champs biologiques complets dans SuiviMedical :
- creatinine, uree, transaminases, hemoglobine, cholesterol
- sources_biologiques (JSONField pour tracer saisie_directe vs analyse_labo)
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suivi_medical', '0008_suivimedical_type_suivi'),
    ]

    operations = [

        # Cardiovasculaire
        migrations.AddField(
            model_name='suivimedical',
            name='cholesterol',
            field=models.FloatField(blank=True, null=True, verbose_name='Cholestérol (g/L)'),
        ),

        # Rénal / hépatique
        migrations.AddField(
            model_name='suivimedical',
            name='creatinine',
            field=models.FloatField(blank=True, null=True, verbose_name='Créatinine (mg/L)'),
        ),
        migrations.AddField(
            model_name='suivimedical',
            name='uree',
            field=models.FloatField(blank=True, null=True, verbose_name='Urée (g/L)'),
        ),
        migrations.AddField(
            model_name='suivimedical',
            name='transaminases',
            field=models.FloatField(blank=True, null=True, verbose_name='Transaminases (UI/L)'),
        ),

        # Hématologique
        migrations.AddField(
            model_name='suivimedical',
            name='hemoglobine',
            field=models.FloatField(blank=True, null=True, verbose_name='Hémoglobine (g/dL)'),
        ),

        # Traçabilité des sources
        migrations.AddField(
            model_name='suivimedical',
            name='sources_biologiques',
            field=models.JSONField(
                blank=True,
                default=dict,
                verbose_name='Sources des mesures biologiques',
            ),
        ),
    ]
