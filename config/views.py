from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from apps.appointments.models import Appointment
from apps.billing.models import Invoice
from apps.patients.models import Patient


@login_required
def dashboard(request):
    today = date.today()
    active_invoices = Invoice.objects.filter(is_void=False, cancel_reason='')

    revenue = active_invoices.aggregate(total=Sum('paid'))['total'] or Decimal('0.00')
    due_total = active_invoices.aggregate(total=Sum('due'))['total'] or Decimal('0.00')

    context = {
        'total_patients': Patient.objects.count(),
        'today_appointments': Appointment.objects.filter(date=today).count(),
        'pending_appointments': Appointment.objects.filter(
            status=Appointment.STATUS_PENDING,
        ).count(),
        'waiting_appointments': Appointment.objects.filter(
            status=Appointment.STATUS_WAITING,
        ).count(),
        'done_appointments': Appointment.objects.filter(
            status=Appointment.STATUS_DONE,
        ).count(),
        'total_invoices': Invoice.objects.count(),
        'revenue': revenue,
        'due_total': due_total,
        'recent_appointments': Appointment.objects.select_related('patient').filter(
            date=today,
        )[:10],
    }
    return render(request, 'dashboard.html', context)
