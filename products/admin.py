from django.contrib import admin
from .models import Product, ProductHistory

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'serial_number', 'purchase_date', 'is_claim_active', 'tstamp')
    search_fields = ('name', 'model', 'serial_number')
    readonly_fields = ('tstamp',)

@admin.register(ProductHistory)
class ProductHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'timestamp', 'details', 'claim_active')
    list_filter = ('timestamp', 'claim_active')
    search_fields = ('product__name', 'details')
