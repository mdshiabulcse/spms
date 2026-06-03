import re
from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class Patient(models.Model):
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHER = 'O'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
    ]

    phone_validator = RegexValidator(
        regex=r'^[0-9+\-\s]{10,22}$',
        message='Phone must be 10–22 characters: digits, spaces, + or - only (e.g. 01711 123456).',
    )

    name = models.CharField(max_length=200, db_index=True)
    phone = models.CharField(max_length=20, db_index=True, validators=[phone_validator])
    date_of_birth = models.DateField(null=True, blank=True, db_index=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return f'{self.name} ({self.phone})'

    def compute_age(self):
        if not self.date_of_birth:
            return self.age
        today = date.today()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @property
    def display_age(self):
        return self.compute_age()

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            self.age = self.compute_age()
        super().save(*args, **kwargs)

    @staticmethod
    def normalize_phone(value):
        if not value:
            return value
        return re.sub(r'\s+', ' ', str(value).strip())
