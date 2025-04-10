# Generated by Django 4.2.9 on 2025-04-09 21:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('chest', models.FloatField(default=100.0)),
                ('half_back', models.FloatField(default=20.0)),
                ('back_neck_to_waist', models.FloatField(default=44.2)),
                ('scye_depth', models.FloatField(default=24.4)),
                ('neck_size', models.FloatField(default=40.0)),
                ('sleeve_length', models.FloatField(default=65.0)),
                ('close_wrist', models.FloatField(default=17.8)),
                ('finished_length', models.FloatField(default=70.0)),
                ('body_rise', models.FloatField(default=28.0)),
                ('inside_leg', models.FloatField(default=92.0)),
                ('seat_measurement', models.FloatField(default=119.0)),
                ('waist_measurement', models.FloatField(default=111.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pattern',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('pattern_type', models.CharField(choices=[('TSHIRT', 'T-Shirt'), ('PANTS', 'Pants'), ('COMBINED', 'Combined Pattern')], max_length=20)),
                ('fit_type', models.CharField(choices=[('STANDARD', 'Standard Fit'), ('EASE', 'Ease Fit')], max_length=20)),
                ('short_sleeve', models.BooleanField(default=False)),
                ('pattern_data', models.JSONField(blank=True, null=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='pattern_pdfs')),
                ('svg_file', models.FileField(blank=True, null=True, upload_to='pattern_svgs')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('measurement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patterns.measurement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PatternPiece',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('svg_content', models.TextField()),
                ('pattern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pieces', to='patterns.pattern')),
            ],
        ),
    ]
