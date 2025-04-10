// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Show loading overlay on form submissions for pattern generation
    const patternForms = document.querySelectorAll('form.pattern-generate-form');
    patternForms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoadingOverlay('Generating your pattern...');
        });
    });

    // Pattern type change handler
    const patternTypeSelect = document.getElementById('id_pattern_type');
    if (patternTypeSelect) {
        patternTypeSelect.addEventListener('change', updateFormFields);
        // Run once on page load
        updateFormFields();
    }

    // Add warning when deleting items
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});

// Show loading overlay with custom message
function showLoadingOverlay(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary spinner" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

// Hide loading overlay
function hideLoadingOverlay() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Update form fields based on pattern type
function updateFormFields() {
    const patternType = document.getElementById('id_pattern_type').value;
    const sleeveOption = document.getElementById('sleeve-option-container');

    if (sleeveOption) {
        if (patternType === 'TSHIRT') {
            sleeveOption.style.display = 'block';
        } else {
            sleeveOption.style.display = 'none';
            // Uncheck the checkbox when not visible
            document.getElementById('id_short_sleeve').checked = false;
        }
    }
}