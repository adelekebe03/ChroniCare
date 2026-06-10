"""
Migration 0007 — Améliorations alertes médicales chroniques :

1. Alert.alert_type   : mise à jour des choices (labels en français)
2. Alert.source       : CharField libre → CharField avec choices métier
3. Alert.level        : supprimé (remplacé par alert_type pour éviter la redondance)
4. Alert.acknowledged_by / acknowledged_at : accusé de réception médecin
5. Alert.resolved_by / resolved_at : traçabilité résolution
6. Alert.source_suivi : FK → SuiviMedical (traçabilité source)
7. Alert.source_labtest : FK → LabTest (traçabilité source)
8. Notification.appointment : CASCADE → SET_NULL (ne pas supprimer la notif si RDV supprimé)
9. Notification.type  : champ supprimé (redondant avec level)
10. MessageTemplate.code : blank=True seulement (null supprimé)
"""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('alertes_notifications', '0006_alert_level'),
        ('suivi_medical', '0009_add_biological_fields'),
        ('laboratoire',   '0010_enforce_business_rules'),
        ('patients',      '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        # ── 1. Alert.alert_type : mise à jour choices ───────────────────────
        migrations.AlterField(
            model_name='alert',
            name='alert_type',
            field=models.CharField(
                choices=[
                    ('critical', 'Critique'),
                    ('warning',  'Avertissement'),
                    ('info',     'Information'),
                ],
                default='warning',
                max_length=20,
                verbose_name='Sévérité',
            ),
        ),

        # ── 2. Alert.source : choices métier ───────────────────────────────
        migrations.AlterField(
            model_name='alert',
            name='source',
            field=models.CharField(
                choices=[
                    ('suivi_medical',   'Suivi médical'),
                    ('laboratoire',     'Laboratoire'),
                    ('stock_pharmacie', 'Stock pharmacie'),
                    ('renouvellement',  'Renouvellement traitement'),
                    ('rdv',             'Rendez-vous'),
                    ('system',          'Système'),
                ],
                default='system',
                max_length=50,
                verbose_name='Source',
            ),
        ),

        # ── 3. Alert.level : suppression (redondant avec alert_type) ────────
        migrations.RemoveField(
            model_name='alert',
            name='level',
        ),

        # ── 4. Alert.acknowledged_by ────────────────────────────────────────
        migrations.AddField(
            model_name='alert',
            name='acknowledged_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='alertes_accusees',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Accusée par',
            ),
        ),

        # ── 5. Alert.acknowledged_at ────────────────────────────────────────
        migrations.AddField(
            model_name='alert',
            name='acknowledged_at',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Accusée le'),
        ),

        # ── 6. Alert.resolved_by ─────────────────────────────────────────────
        migrations.AddField(
            model_name='alert',
            name='resolved_by',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='alertes_resolues',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Résolue par',
            ),
        ),

        # ── 7. Alert.resolved_at ─────────────────────────────────────────────
        migrations.AddField(
            model_name='alert',
            name='resolved_at',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Résolue le'),
        ),

        # ── 8. Alert.source_suivi ────────────────────────────────────────────
        migrations.AddField(
            model_name='alert',
            name='source_suivi',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='alertes',
                to='suivi_medical.suivimedical',
                verbose_name='Suivi médical lié',
            ),
        ),

        # ── 9. Alert.source_labtest ──────────────────────────────────────────
        migrations.AddField(
            model_name='alert',
            name='source_labtest',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='alertes',
                to='laboratoire.labtest',
                verbose_name='Analyse liée',
            ),
        ),

        # ── 10. Notification.appointment : CASCADE → SET_NULL ─────────────
        migrations.AlterField(
            model_name='notification',
            name='appointment',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='notifications',
                to='appointments.appointment',
                verbose_name='Rendez-vous lié',
            ),
        ),

        # ── 11. Notification.type : suppression ──────────────────────────────
        migrations.RemoveField(
            model_name='notification',
            name='type',
        ),

        # ── 12. MessageTemplate.code : null=True → blank=True seulement ──────
        migrations.AlterField(
            model_name='messagetemplate',
            name='code',
            field=models.SlugField(blank=True, unique=True, verbose_name='Code unique'),
        ),
    ]
