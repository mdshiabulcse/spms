from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import (
    require_delete_patients,
    require_patients_section,
    require_write_patients,
)

from .forms import PatientForm
from .models import Patient


@login_required
@require_patients_section
def patient_list(request):
    query = request.GET.get('q', '').strip()
    patients = Patient.objects.all()
    if query:
        filters = Q(name__icontains=query) | Q(phone__icontains=query)
        if query.isdigit():
            filters |= Q(pk=int(query))
        patients = patients.filter(filters)
    return render(request, 'patients/patient_list.html', {
        'patients': patients,
        'query': query,
    })


@login_required
@require_patients_section
@require_write_patients
def patient_form(request, pk=None):
    patient = get_object_or_404(Patient, pk=pk) if pk else None
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            action = 'updated' if pk else 'created'
            messages.success(request, f'Patient {action} successfully.')
            return redirect('patients:patient_list')
    else:
        form = PatientForm(instance=patient)
    context = {
        'form': form,
        'patient': patient,
        'is_edit': pk is not None,
    }
    if patient:
        context['appointment_count'] = patient.appointments.count()
    return render(request, 'patients/patient_form.html', context)


@login_required
@require_patients_section
@require_delete_patients
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        try:
            patient.delete()
            messages.success(request, 'Patient deleted successfully.')
        except Exception:
            messages.error(
                request,
                'Cannot delete patient with existing appointments.',
            )
        return redirect('patients:patient_list')
    return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})
