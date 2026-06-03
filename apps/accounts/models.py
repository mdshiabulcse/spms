from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Clinic role for each staff user (Django auth user)."""

    ROLE_ADMIN = 'admin'
    ROLE_RECEPTION = 'reception'
    ROLE_BILLING = 'billing'
    ROLE_VIEWER = 'viewer'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Clinic admin'),
        (ROLE_RECEPTION, 'Reception'),
        (ROLE_BILLING, 'Billing'),
        (ROLE_VIEWER, 'Viewer (read-only)'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clinic_profile',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_RECEPTION)

    class Meta:
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'

    def __str__(self):
        return f'{self.user.get_username()} — {self.get_role_display()}'
