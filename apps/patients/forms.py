import re
from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'phone', 'date_of_birth', 'gender', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Fatima Rahman',
                'autocomplete': 'name',
                'autofocus': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 01711 123456',
                'inputmode': 'tel',
                'autocomplete': 'tel',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'max': date.today().isoformat(),
            }),
            'gender': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'House / area, city (optional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_new = not (self.instance and self.instance.pk)

        self.fields['name'].label = 'Full name'
        self.fields['name'].help_text = 'As shown on clinic records and invoices.'
        self.fields['name'].required = True

        self.fields['phone'].label = 'Mobile phone'
        self.fields['phone'].help_text = '10–15 digits; spaces, + or - allowed.'
        self.fields['phone'].required = True

        self.fields['date_of_birth'].label = 'Date of birth'
        self.fields['date_of_birth'].help_text = (
            'Required for new patients. Age is calculated automatically.'
        )
        self.fields['date_of_birth'].required = is_new

        self.fields['gender'].label = 'Gender'
        self.fields['gender'].required = True

        self.fields['address'].label = 'Address'
        self.fields['address'].help_text = 'Optional — useful for follow-up and reports.'
        self.fields['address'].required = False

    def clean_phone(self):
        phone = Patient.normalize_phone(self.cleaned_data.get('phone', ''))
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise ValidationError('Enter at least 10 digits for the phone number.')
        if len(digits) > 15:
            raise ValidationError('Phone number is too long (max 15 digits).')
        return phone

    def clean(self):
        data = super().clean()
        dob = data.get('date_of_birth')
        is_new = not (self.instance and self.instance.pk)

        if is_new and not dob:
            raise ValidationError({'date_of_birth': 'Date of birth is required for new patients.'})
        if dob and dob > date.today():
            raise ValidationError({'date_of_birth': 'Date of birth cannot be in the future.'})
        return data
