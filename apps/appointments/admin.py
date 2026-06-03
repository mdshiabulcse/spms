from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'date', 'serial_no', 'status')
    list_filter = ('status', 'date')
    search_fields = ('patient__name', 'patient__phone')
