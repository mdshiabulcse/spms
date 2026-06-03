from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.utils.dateparse import parse_date

from apps.patients.models import Patient


class Appointment(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_WAITING = 'WAITING'
    STATUS_DONE = 'DONE'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_WAITING, 'Waiting'),
        (STATUS_DONE, 'Done'),
    ]

    STATUS_FLOW = {
        STATUS_PENDING: STATUS_WAITING,
        STATUS_WAITING: STATUS_DONE,
        STATUS_DONE: None,
    }

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name='appointments',
    )
    date = models.DateField(db_index=True)
    serial_no = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'serial_no']
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'serial_no'],
                name='unique_appointment_serial_per_day',
            ),
        ]

    def __str__(self):
        return f'#{self.serial_no} - {self.patient.name} ({self.date})'

    @classmethod
    def next_serial_for_date(cls, d):
        if d is None:
            d = date.today()
        if isinstance(d, str):
            d = parse_date(d)
        if d is None:
            d = date.today()
        current = cls.objects.filter(date=d).aggregate(m=Max('serial_no'))['m']
        return (current or 0) + 1

    def get_next_status(self):
        return self.STATUS_FLOW.get(self.status)

    def can_advance_status(self):
        return self.get_next_status() is not None

    def advance_status(self):
        next_status = self.get_next_status()
        if not next_status:
            raise ValidationError('Appointment is already at final status.')
        self.status = next_status
        self.save(update_fields=['status'])

    def clean(self):
        super().clean()
        if self.pk:
            old = Appointment.objects.filter(pk=self.pk).first()
            if old and old.status != self.status:
                allowed = old.get_next_status()
                if self.status != allowed:
                    raise ValidationError(
                        f'Invalid status transition: {old.status} → {self.status}. '
                        f'Allowed next: {allowed or "none"}.'
                    )
