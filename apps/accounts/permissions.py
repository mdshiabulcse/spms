from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import UserProfile


def _profile(user):
    if not user.is_authenticated:
        return None
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'role': UserProfile.ROLE_ADMIN if user.is_superuser else UserProfile.ROLE_RECEPTION,
        },
    )
    return profile


def get_profile(user):
    return _profile(user)


def is_super_admin(user):
    return bool(user.is_authenticated and user.is_superuser)


def is_viewer(user):
    p = _profile(user)
    return bool(p and p.role == UserProfile.ROLE_VIEWER)


def is_clinic_admin(user):
    """Full app access except Django superuser extras."""
    p = _profile(user)
    return bool(
        user.is_authenticated
        and (user.is_superuser or (p and p.role == UserProfile.ROLE_ADMIN)),
    )


def can_write_patients(user):
    if not user.is_authenticated:
        return False
    if is_super_admin(user) or is_clinic_admin(user):
        return True
    p = _profile(user)
    return bool(p and p.role == UserProfile.ROLE_RECEPTION)


def can_delete_patients(user):
    return is_super_admin(user) or is_clinic_admin(user)


def can_manage_appointments(user):
    if not user.is_authenticated:
        return False
    if is_super_admin(user) or is_clinic_admin(user):
        return True
    p = _profile(user)
    return bool(p and p.role in (UserProfile.ROLE_RECEPTION, UserProfile.ROLE_VIEWER))


def can_edit_appointments(user):
    if is_viewer(user):
        return False
    if is_super_admin(user) or is_clinic_admin(user):
        return True
    p = _profile(user)
    return bool(p and p.role == UserProfile.ROLE_RECEPTION)


def can_access_patients_section(user):
    if not user.is_authenticated:
        return False
    if is_super_admin(user) or is_clinic_admin(user):
        return True
    p = _profile(user)
    return bool(p and p.role in (UserProfile.ROLE_RECEPTION, UserProfile.ROLE_VIEWER))


def can_access_appointments_section(user):
    return can_manage_appointments(user)


def can_manage_billing(user):
    if not user.is_authenticated:
        return False
    if is_super_admin(user) or is_clinic_admin(user):
        return True
    p = _profile(user)
    return bool(p and p.role in (UserProfile.ROLE_BILLING, UserProfile.ROLE_VIEWER))


def can_access_billing_section(user):
    return can_manage_billing(user)


def can_edit_billing(user):
    if is_viewer(user):
        return False
    if is_super_admin(user) or is_clinic_admin(user):
        return True
    p = _profile(user)
    return bool(p and p.role == UserProfile.ROLE_BILLING)


def role_badge_label(user):
    if is_super_admin(user):
        return 'Super admin'
    p = _profile(user)
    return p.get_role_display() if p else ''


def deny(request, msg='You do not have permission for this action.'):
    messages.error(request, msg)
    return redirect('dashboard')


def require_write_patients(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_write_patients(request.user):
            return deny(request)
        return view_func(request, *args, **kwargs)

    return _wrapped


def require_delete_patients(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_delete_patients(request.user):
            return deny(request, 'Only clinic admins can delete patients.')
        return view_func(request, *args, **kwargs)

    return _wrapped


def require_edit_appointments(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_edit_appointments(request.user):
            return deny(request, 'You do not have permission to change appointments.')
        return view_func(request, *args, **kwargs)

    return _wrapped


def require_edit_billing(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_edit_billing(request.user):
            return deny(request, 'You do not have permission to edit invoices.')
        return view_func(request, *args, **kwargs)

    return _wrapped


def require_billing_section(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_access_billing_section(request.user):
            return deny(request, 'You do not have access to billing.')
        return view_func(request, *args, **kwargs)

    return _wrapped


def require_patients_section(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_access_patients_section(request.user):
            return deny(request, 'You do not have access to patients.')
        return view_func(request, *args, **kwargs)

    return _wrapped


def require_appointments_section(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not can_access_appointments_section(request.user):
            return deny(request, 'You do not have access to appointments.')
        return view_func(request, *args, **kwargs)

    return _wrapped
