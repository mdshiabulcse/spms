from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'appointment', 'total', 'discount', 'paid', 'due',
        'status', 'is_void', 'refund_amount', 'created_at',
    )
    list_filter = ('status', 'is_void')
    search_fields = ('appointment__patient__name',)
