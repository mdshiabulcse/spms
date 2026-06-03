from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from apps.accounts.permissions import require_edit_appointments, require_appointments_section
from apps.patients.models import Patient

from .forms import AppointmentForm
from .models import Appointment


@login_required
@require_appointments_section
def appointment_list(request):
    status_filter = request.GET.get('status', '').strip()
    appointments = Appointment.objects.select_related('patient', 'invoice').all()
    if status_filter in dict(Appointment.STATUS_CHOICES):
        appointments = appointments.filter(status=status_filter)
    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    })


@login_required
@require_appointments_section
@require_edit_appointments
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = Appointment.STATUS_PENDING
            appointment.save()
            messages.success(request, 'Appointment created successfully.')
            return redirect('appointments:appointment_list')
    else:
        initial = {}
        raw_date = request.GET.get('date')
        if raw_date:
            d = parse_date(raw_date)
            if d:
                initial['date'] = d
        if not initial.get('date'):
            initial['date'] = date.today()
        initial['serial_no'] = Appointment.next_serial_for_date(initial['date'])
        raw_patient = request.GET.get('patient')
        if raw_patient and raw_patient.isdigit():
            patient = Patient.objects.filter(pk=int(raw_patient)).first()
            if patient:
                initial['patient'] = patient.pk
        form = AppointmentForm(initial=initial)
    return render(request, 'appointments/appointment_form.html', {'form': form})


@login_required
@require_appointments_section
@require_edit_appointments
def appointment_status_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        try:
            appointment.advance_status()
            messages.success(
                request,
                f'Appointment status updated to {appointment.get_status_display()}.',
            )
        except Exception as exc:
            messages.error(request, str(exc))
    return redirect('appointments:appointment_list')
