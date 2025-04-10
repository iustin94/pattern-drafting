# dashboard/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from patterns.models import Pattern, Measurement


@login_required
def dashboard(request):
    """Main dashboard view showing user's patterns and measurements"""
    patterns = Pattern.objects.filter(user=request.user).order_by('-updated_at')
    measurements = Measurement.objects.filter(user=request.user).order_by('-updated_at')

    context = {
        'patterns': patterns,
        'measurements': measurements,
        'patterns_count': patterns.count(),
        'measurements_count': measurements.count(),
    }

    return render(request, 'dashboard/dashboard.html', context)