from decimal import Decimal

from django import forms

from apps.appointments.models import Appointment

from .models import Invoice


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['appointment', 'total', 'discount']
        widgets = {
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'total': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg text-end',
                'step': '0.01',
                'min': '0',
                'inputmode': 'decimal',
                'placeholder': '0.00',
                'autofocus': True,
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control text-end',
                'step': '0.01',
                'min': '0',
                'inputmode': 'decimal',
                'placeholder': '0.00',
            }),
        }

    def __init__(self, *args, appointment=None, **kwargs):
        super().__init__(*args, **kwargs)
        if appointment is None:
            raise ValueError('appointment is required')
        self.fixed_appointment = appointment
        self.fields['appointment'].queryset = Appointment.objects.filter(pk=appointment.pk)
        self.fields['appointment'].initial = appointment.pk
        self.fields['appointment'].widget = forms.HiddenInput()
        self.fields['total'].label = 'Total amount'
        self.fields['discount'].label = 'Discount'
        self.fields['discount'].help_text = 'Subtracted from total. Paid amount updates automatically.'
        if not self.is_bound:
            self.fields['discount'].initial = Decimal('0.00')

    @staticmethod
    def calculate_paid(total, discount):
        total = total if total is not None else Decimal('0.00')
        discount = discount if discount is not None else Decimal('0.00')
        return max(total - discount, Decimal('0.00'))

    def clean(self):
        cleaned = super().clean()
        total = cleaned.get('total')
        discount = cleaned.get('discount')
        if total is not None and discount is not None and discount > total:
            self.add_error('discount', 'Discount cannot exceed total amount.')
        return cleaned

    def clean_appointment(self):
        appointment = self.cleaned_data['appointment']
        if hasattr(appointment, 'invoice') and (
            not self.instance.pk or appointment.invoice.pk != self.instance.pk
        ):
            raise forms.ValidationError('This appointment already has an invoice.')
        return appointment

    def save(self, commit=True):
        invoice = super().save(commit=False)
        invoice.paid = self.calculate_paid(invoice.total, invoice.discount)
        if commit:
            invoice.save()
        return invoice


class PaymentUpdateForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['paid', 'discount', 'refund_amount']
        widgets = {
            'paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'refund_amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
        }


class CancelInvoiceForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Cancellation reason',
    )
