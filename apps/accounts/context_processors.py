from . import permissions


def clinic_roles(request):
    user = request.user
    if not user.is_authenticated:
        return {
            'clinic_profile': None,
            'role_display': '',
            'can_write_patients': False,
            'can_delete_patients': False,
            'can_edit_appointments': False,
            'can_manage_billing_nav': False,
            'can_edit_billing': False,
            'is_super_admin': False,
            'is_clinic_admin': False,
            'user_display_name': '',
            'show_patients_nav': False,
            'show_appointments_nav': False,
            'show_billing_nav': False,
        }
    profile = permissions.get_profile(user)
    return {
        'clinic_profile': profile,
        'role_display': permissions.role_badge_label(user),
        'can_write_patients': permissions.can_write_patients(user),
        'can_delete_patients': permissions.can_delete_patients(user),
        'can_edit_appointments': permissions.can_edit_appointments(user),
        'can_manage_billing_nav': permissions.can_manage_billing(user),
        'can_edit_billing': permissions.can_edit_billing(user),
        'is_super_admin': permissions.is_super_admin(user),
        'is_clinic_admin': permissions.is_clinic_admin(user),
        'user_display_name': user.get_full_name() or user.get_username(),
        'show_patients_nav': permissions.can_access_patients_section(user),
        'show_appointments_nav': permissions.can_access_appointments_section(user),
        'show_billing_nav': permissions.can_access_billing_section(user),
        'is_viewer': permissions.is_viewer(user),
    }
