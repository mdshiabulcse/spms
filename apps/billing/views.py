from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import (
    can_edit_billing,
    deny,
    require_billing_section,
    require_edit_billing,
)
from apps.appointments.models import Appointment

from .forms import CancelInvoiceForm, InvoiceForm, PaymentUpdateForm
from .models import Invoice


def _appointment_for_invoice_create(request):
    raw = (
        request.POST.get('appointment')
        if request.method == 'POST'
        else request.GET.get('appointment')
    )
    if not raw or not str(raw).isdigit():
        return None
    return Appointment.objects.select_related('patient').filter(pk=int(raw)).first()


@login_required
@require_billing_section
def invoice_list(request):
    status_filter = request.GET.get('status', '').strip()
    invoices = Invoice.objects.select_related(
        'appointment__patient',
    ).all()
    if status_filter in dict(Invoice.STATUS_CHOICES):
        invoices = invoices.filter(status=status_filter)
    void_filter = request.GET.get('void', '')
    if void_filter == '1':
        invoices = invoices.filter(is_void=True)
    elif void_filter == '0':
        invoices = invoices.filter(is_void=False)
    return render(request, 'billing/invoice_list.html', {
        'invoices': invoices,
        'status_filter': status_filter,
        'status_choices': Invoice.STATUS_CHOICES,
    })


@login_required
@require_billing_section
@require_edit_billing
def invoice_create(request):
    appointment = _appointment_for_invoice_create(request)
    if appointment is None:
        messages.error(
            request,
            'Create invoices from the Appointments list using “Create invoice” on a visit.',
        )
        return redirect('appointments:appointment_list')

    if hasattr(appointment, 'invoice'):
        messages.error(request, 'This appointment already has an invoice.')
        return redirect('appointments:appointment_list')

    if request.method == 'POST':
        form = InvoiceForm(request.POST, appointment=appointment)
        if form.is_valid():
            inv = form.save()
            messages.success(
                request,
                'Invoice created. You can print the simple invoice below.',
            )
            return redirect('billing:invoice_simple', pk=inv.pk)
    else:
        form = InvoiceForm(appointment=appointment)

    return render(request, 'billing/invoice_form.html', {
        'form': form,
        'appointment': appointment,
        'patient': appointment.patient,
    })


@login_required
@require_billing_section
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('appointment__patient'),
        pk=pk,
    )
    payment_form = PaymentUpdateForm(instance=invoice)
    cancel_form = CancelInvoiceForm()

    if request.method == 'POST':
        if not can_edit_billing(request.user):
            return deny(request, 'You can view invoices but not change payments.')

        action = request.POST.get('action')
        if invoice.is_locked:
            messages.error(request, 'This invoice is void or cancelled and cannot be edited.')
            return redirect('billing:invoice_detail', pk=pk)

        if action == 'payment':
            payment_form = PaymentUpdateForm(request.POST, instance=invoice)
            if payment_form.is_valid():
                try:
                    payment_form.save()
                    messages.success(request, 'Payment updated successfully.')
                    return redirect('billing:invoice_detail', pk=pk)
                except ValidationError as exc:
                    messages.error(request, exc.message if hasattr(exc, 'message') else str(exc))
            else:
                messages.error(request, 'Please correct payment form errors.')

        elif action == 'cancel':
            cancel_form = CancelInvoiceForm(request.POST)
            if cancel_form.is_valid():
                try:
                    invoice.cancel(cancel_form.cleaned_data['reason'])
                    messages.success(request, 'Invoice cancelled successfully.')
                    return redirect('billing:invoice_detail', pk=pk)
                except ValidationError as exc:
                    messages.error(request, str(exc))

    return render(request, 'billing/invoice_detail.html', {
        'invoice': invoice,
        'payment_form': payment_form,
        'cancel_form': cancel_form,
    })


@login_required
@require_billing_section
def invoice_simple(request, pk):
    """Print-friendly simple invoice for one appointment."""
    invoice = get_object_or_404(
        Invoice.objects.select_related('appointment__patient'),
        pk=pk,
    )
    return render(request, 'billing/invoice_simple.html', {
        'invoice': invoice,
    })


@login_required
@require_billing_section
@require_edit_billing
def invoice_void(request):
    if request.method != 'POST':
        return redirect('billing:invoice_list')
    invoice_id = request.POST.get('invoice_id')
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    try:
        invoice.void()
        messages.success(request, f'Invoice #{invoice.pk} voided successfully.')
    except ValidationError as exc:
        messages.error(request, str(exc))
    return redirect('billing:invoice_list')
