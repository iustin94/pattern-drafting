# patterns/views.py

import os
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.files.base import ContentFile

from .models import Pattern, Measurement, PatternPiece
from .forms import MeasurementForm, PatternCreateForm
from .pattern_engine.src.pant.Drafter import PantDrafter
from .pattern_engine.src.tshirt.Drafter import TShirtDrafter
from .pattern_engine.src.TechnicalPatternRenderer import TechnicalPatternRenderer


@login_required
def measurement_list(request):
    """View all user measurements"""
    measurements = Measurement.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'patterns/measurement_list.html', {'measurements': measurements})


@login_required
def measurement_create(request):
    """Create a new set of measurements"""
    if request.method == 'POST':
        form = MeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.user = request.user
            measurement.save()
            messages.success(request, f'Your measurements "{measurement.name}" have been saved!')
            return redirect('measurement_list')
    else:
        form = MeasurementForm()

    return render(request, 'patterns/measurement_form.html', {'form': form, 'title': 'Create Measurements'})


@login_required
def measurement_update(request, pk):
    """Update an existing set of measurements"""
    measurement = get_object_or_404(Measurement, pk=pk, user=request.user)

    if request.method == 'POST':
        form = MeasurementForm(request.POST, instance=measurement)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your measurements "{measurement.name}" have been updated!')
            return redirect('measurement_list')
    else:
        form = MeasurementForm(instance=measurement)

    return render(request, 'patterns/measurement_form.html', {'form': form, 'title': 'Update Measurements'})


@login_required
def measurement_delete(request, pk):
    """Delete a set of measurements"""
    measurement = get_object_or_404(Measurement, pk=pk, user=request.user)

    if request.method == 'POST':
        measurement.delete()
        messages.success(request, 'Your measurements have been deleted!')
        return redirect('measurement_list')

    return render(request, 'patterns/measurement_confirm_delete.html', {'measurement': measurement})


@login_required
def pattern_list(request):
    """View all user patterns"""
    patterns = Pattern.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'patterns/pattern_list.html', {'patterns': patterns})


@login_required
def pattern_create(request):
    """Create a new pattern"""
    if request.method == 'POST':
        form = PatternCreateForm(request.POST, user=request.user)
        if form.is_valid():
            pattern = form.save(commit=False)
            pattern.user = request.user
            pattern.save()

            # Generate the pattern based on the selection
            generate_pattern(pattern)

            messages.success(request, f'Your pattern "{pattern.name}" has been created!')
            return redirect('pattern_detail', pk=pattern.pk)
    else:
        form = PatternCreateForm(user=request.user)

    return render(request, 'patterns/pattern_form.html', {'form': form, 'title': 'Create Pattern'})


@login_required
def pattern_detail(request, pk):
    """View pattern details and download options"""
    pattern = get_object_or_404(Pattern, pk=pk, user=request.user)
    pieces = PatternPiece.objects.filter(pattern=pattern)

    return render(request, 'patterns/pattern_detail.html', {
        'pattern': pattern,
        'pieces': pieces
    })


@login_required
def pattern_delete(request, pk):
    """Delete a pattern"""
    pattern = get_object_or_404(Pattern, pk=pk, user=request.user)

    if request.method == 'POST':
        pattern.delete()
        messages.success(request, 'Your pattern has been deleted!')
        return redirect('pattern_list')

    return render(request, 'patterns/pattern_confirm_delete.html', {'pattern': pattern})


@login_required
def download_pdf(request, pk):
    """Download pattern as PDF"""
    pattern = get_object_or_404(Pattern, pk=pk, user=request.user)

    if pattern.pdf_file:
        response = HttpResponse(pattern.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pattern.name}.pdf"'
        return response

    messages.error(request, 'PDF file not found for this pattern.')
    return redirect('pattern_detail', pk=pattern.pk)


@login_required
def download_svg(request, pk, piece_id=None):
    """Download pattern piece as SVG or all pieces as ZIP"""
    pattern = get_object_or_404(Pattern, pk=pk, user=request.user)

    if piece_id:
        piece = get_object_or_404(PatternPiece, pk=piece_id, pattern=pattern)
        response = HttpResponse(piece.svg_content, content_type='image/svg+xml')
        response['Content-Disposition'] = f'attachment; filename="{pattern.name}_{piece.name}.svg"'
        return response

    # If no piece_id is provided, redirect to pattern detail
    return redirect('pattern_detail', pk=pattern.pk)


def generate_pattern(pattern):
    """Generate the pattern files using the pattern drafting engine"""

    # Get measurements
    measurement_model = pattern.measurement
    measurements = measurement_model.as_dict()

    # Temporary directory for generated files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Determine which drafter to use based on pattern type
        if pattern.pattern_type == 'TSHIRT':
            ease_fitting = pattern.fit_type == 'EASE'
            short_sleeve = pattern.short_sleeve

            # Create drafter
            drafter = TShirtDrafter(measurements, ease_fitting=ease_fitting, short_sleeve=short_sleeve)
            pattern_obj = drafter.draft()

        elif pattern.pattern_type == 'PANTS':
            ease_fitting = pattern.fit_type == 'EASE'

            # Create pant drafter
            drafter = PantDrafter(measurements, ease_fitting=ease_fitting)
            pattern_obj = drafter.draft()

        else:
            # Combined pattern - you could implement this based on your needs
            messages.error(pattern.user, 'Combined patterns not implemented yet')
            return

        # Create renderer
        renderer = TechnicalPatternRenderer(pattern_obj)

        # Generate PDF
        pdf_path = os.path.join(temp_dir, f"{pattern.name}_technical.pdf")
        renderer.export_pdf(pdf_path)

        # Save PDF to the model
        with open(pdf_path, 'rb') as f:
            pattern.pdf_file.save(f"{pattern.name}_technical.pdf", ContentFile(f.read()), save=False)

        # Generate SVG files for each piece
        for piece_name, piece in pattern_obj.pieces.items():
            svg_path = os.path.join(temp_dir, f"{pattern.name}_{piece_name}.svg")

            # Export the piece as SVG
            with open(svg_path, 'w') as f:
                # Calculate bounding box
                min_point, max_point = piece.get_bounding_box()
                padding = 5
                width = max_point.x - min_point.x + 2 * padding
                height = max_point.y - min_point.y + 2 * padding

                # Write SVG header
                f.write(f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
                f.write(f'<svg xmlns="http://www.w3.org/2000/svg" ')
                f.write(f'viewBox="{min_point.x - padding} {min_point.y - padding} {width} {height}" ')
                f.write(f'width="{width}mm" height="{height}mm" preserveAspectRatio="xMidYMid meet">\n')
                f.write(f'<title>{piece_name}</title>\n')

                # Draw paths
                color = renderer.colors.get(piece_name, 'black')

                for path in piece.paths:
                    for segment in path:
                        if hasattr(segment, 'start') and hasattr(segment, 'end'):
                            # Draw line segment
                            f.write(f'<line x1="{segment.start.x}" y1="{segment.start.y}" ')
                            f.write(f'x2="{segment.end.x}" y2="{segment.end.y}" ')
                            f.write(f'stroke="{color}" stroke-width="0.5mm" />\n')
                        elif hasattr(segment, 'as_tuple_list'):
                            # Handle curve segments
                            points = segment.as_tuple_list(30)

                            if len(points) >= 2:
                                # Create polyline for the curve
                                points_str = " ".join([f"{x},{y}" for x, y in points])
                                f.write(f'<polyline points="{points_str}" ')
                                f.write(f'fill="none" stroke="{color}" stroke-width="0.5mm" />\n')

                # Close the SVG tag
                f.write('</svg>\n')

            # Create pattern piece record
            with open(svg_path, 'r') as f:
                svg_content = f.read()
                PatternPiece.objects.create(
                    pattern=pattern,
                    name=piece_name,
                    svg_content=svg_content
                )

        # Store the pattern data as JSON (for potential future use)
        pattern.pattern_data = {
            'type': pattern.pattern_type,
            'fit': pattern.fit_type,
            'short_sleeve': pattern.short_sleeve,
            'measurements': measurements
        }
        pattern.save()