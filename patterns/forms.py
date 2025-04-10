# patterns/forms.py

from django import forms
from .models import Pattern, Measurement


class MeasurementForm(forms.ModelForm):
    """Form for creating and editing body measurements"""

    class Meta:
        model = Measurement
        fields = [
            'name', 'chest', 'half_back', 'back_neck_to_waist',
            'scye_depth', 'neck_size', 'sleeve_length',
            'close_wrist', 'finished_length', 'body_rise',
            'inside_leg', 'seat_measurement', 'waist_measurement'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'chest': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'half_back': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'back_neck_to_waist': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'scye_depth': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'neck_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'sleeve_length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'close_wrist': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'finished_length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'body_rise': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'inside_leg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'seat_measurement': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'waist_measurement': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }


class PatternCreateForm(forms.ModelForm):
    """Form for creating a new pattern"""

    class Meta:
        model = Pattern
        fields = ['name', 'description', 'pattern_type', 'fit_type', 'short_sleeve', 'measurement']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pattern_type': forms.Select(attrs={'class': 'form-control'}),
            'fit_type': forms.Select(attrs={'class': 'form-control'}),
            'short_sleeve': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'measurement': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PatternCreateForm, self).__init__(*args, **kwargs)

        if user:
            # Filter measurements to show only the current user's
            self.fields['measurement'].queryset = Measurement.objects.filter(user=user)