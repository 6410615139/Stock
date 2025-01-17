from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'serial_number', 'purchase_date', 'warranty_period', 'is_claim_active', 'tstamp')
    list_filter = ('purchase_date', 'warranty_period', 'tstamp')
    search_fields = ('name', 'model', 'serial_number')
    readonly_fields = ('tstamp',)

    def is_claim_active(self, obj):
        return obj.is_claim_active()
    is_claim_active.boolean = True  # Display as a boolean in the admin
