from django import forms
from django.core.exceptions import ValidationError

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'date', 'serial_no', 'note']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'serial_no': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Unique number for this date',
            }),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = self.fields['patient'].queryset.order_by('name')
        self.fields['serial_no'].help_text = (
            'Each visit on the same day must use a different serial (queue) number.'
        )

    def clean(self):
        cleaned = super().clean()
        appt_date = cleaned.get('date')
        serial = cleaned.get('serial_no')
        if appt_date is not None and serial is not None:
            qs = Appointment.objects.filter(date=appt_date, serial_no=serial)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                nxt = Appointment.next_serial_for_date(appt_date)
                raise ValidationError({
                    'serial_no': (
                        f'Serial {serial} is already used on {appt_date}. '
                        f'Try the next available serial: {nxt}.'
                    ),
                })
        return cleaned
