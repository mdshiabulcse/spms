from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'date_of_birth', 'age', 'gender', 'created_at')
    search_fields = ('name', 'phone')
    list_filter = ('gender',)
