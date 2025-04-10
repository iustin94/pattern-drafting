from django.db import models
from django.conf import settings
import json


class Measurement(models.Model):
    """Model to store user's body measurements"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    # Measurement values
    chest = models.FloatField(default=100.0)
    half_back = models.FloatField(default=20.0)
    back_neck_to_waist = models.FloatField(default=44.2)
    scye_depth = models.FloatField(default=24.4)
    neck_size = models.FloatField(default=40.0)
    sleeve_length = models.FloatField(default=65.0)
    close_wrist = models.FloatField(default=17.8)
    finished_length = models.FloatField(default=70.0)

    # pant measurements
    body_rise = models.FloatField(default=28.0)
    inside_leg = models.FloatField(default=92.0)
    seat_measurement = models.FloatField(default=119.0)
    waist_measurement = models.FloatField(default=111.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def as_dict(self):
        """Convert to dictionary for pattern drafting"""
        return {
            'chest': self.chest,
            'half_back': self.half_back,
            'back_neck_to_waist': self.back_neck_to_waist,
            'scye_depth': self.scye_depth,
            'neck_size': self.neck_size,
            'sleeve_length': self.sleeve_length,
            'close_wrist': self.close_wrist,
            'finished_length': self.finished_length,
            'body_rise': self.body_rise,
            'inside_leg': self.inside_leg,
            'seat_measurement': self.seat_measurement,
            'waist_measurement': self.waist_measurement,
        }


class Pattern(models.Model):
    """Model to store a created pattern"""
    PATTERN_TYPES = [
        ('TSHIRT', 'T-Shirt'),
        ('PANTS', 'Pants'),
        ('COMBINED', 'Combined Pattern'),
    ]

    FIT_TYPES = [
        ('STANDARD', 'Standard Fit'),
        ('EASE', 'Ease Fit'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES)
    fit_type = models.CharField(max_length=20, choices=FIT_TYPES)

    # For T-Shirts
    short_sleeve = models.BooleanField(default=False)

    # Reference to measurements
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)

    # JSON data for pattern pieces
    pattern_data = models.JSONField(blank=True, null=True)

    # Files
    pdf_file = models.FileField(upload_to='pattern_pdfs', blank=True, null=True)
    svg_file = models.FileField(upload_to='pattern_svgs', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PatternPiece(models.Model):
    """Model to store individual pattern pieces"""
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE, related_name='pieces')
    name = models.CharField(max_length=100)
    svg_content = models.TextField()  # Store the SVG content directly

    def __str__(self):
        return f"{self.name} - {self.pattern.name}"