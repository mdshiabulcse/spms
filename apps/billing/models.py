from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.appointments.models import Appointment


class Invoice(models.Model):
    STATUS_UNPAID = 'UNPAID'
    STATUS_PARTIAL = 'PARTIAL'
    STATUS_PAID = 'PAID'
    STATUS_CHOICES = [
        (STATUS_UNPAID, 'Unpaid'),
        (STATUS_PARTIAL, 'Partial'),
        (STATUS_PAID, 'Paid'),
    ]

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.PROTECT,
        related_name='invoice',
    )
    total = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_UNPAID,
        db_index=True,
    )
    is_void = models.BooleanField(default=False, db_index=True)
    cancel_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Invoice #{self.pk} - {self.appointment.patient.name}'

    @property
    def is_cancelled(self):
        return bool(self.cancel_reason.strip())

    @property
    def is_locked(self):
        return self.is_void or self.is_cancelled

    def net_total(self):
        return self.total - self.discount

    def calculate_due(self):
        net = self.net_total()
        due = net - self.paid + self.refund_amount
        return max(due, Decimal('0.00'))

    def update_payment_status(self):
        net = self.net_total()
        effective_paid = self.paid - self.refund_amount
        if effective_paid <= 0:
            self.status = self.STATUS_UNPAID
        elif effective_paid >= net:
            self.status = self.STATUS_PAID
        else:
            self.status = self.STATUS_PARTIAL

    def recalculate(self):
        self.due = self.calculate_due()
        self.update_payment_status()

    def clean(self):
        super().clean()
        for field_name in ('total', 'discount', 'paid', 'refund_amount'):
            value = getattr(self, field_name)
            if value is not None and value < 0:
                raise ValidationError({field_name: 'Cannot be negative.'})

        if self.discount and self.total and self.discount > self.total:
            raise ValidationError({'discount': 'Discount cannot exceed total.'})

        if self.refund_amount > self.paid:
            raise ValidationError({'refund_amount': 'Refund cannot exceed paid amount.'})

        if self.pk and self.is_locked:
            old = Invoice.objects.filter(pk=self.pk).first()
            if old and old.is_locked:
                locked_fields = ('total', 'discount', 'paid', 'refund_amount')
                for field in locked_fields:
                    if getattr(old, field) != getattr(self, field):
                        raise ValidationError('Void or cancelled invoices cannot be edited.')

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        self.recalculate()
        super().save(*args, **kwargs)

    def void(self):
        if self.is_void:
            raise ValidationError('Invoice is already void.')
        self.is_void = True
        self.save(update_fields=['is_void', 'due', 'status', 'updated_at'])

    def cancel(self, reason):
        if not reason or not reason.strip():
            raise ValidationError('Cancel reason is required.')
        if self.is_void:
            raise ValidationError('Cannot cancel a void invoice.')
        self.cancel_reason = reason.strip()
        self.save(update_fields=['cancel_reason', 'updated_at'])
