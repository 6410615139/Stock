from django.contrib import admin
from .models import Product, Serial, Transaction, Branch, BranchProduct


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'EAN_code', 'description', 'dealer_price', 'volumn_price', 'MSRP')
    search_fields = ('brand', 'model', 'EAN_code')
    list_filter = ('brand',)


@admin.register(Serial)
class SerialAdmin(admin.ModelAdmin):
    list_display = ('serial', 'product')
    search_fields = ('serial', 'product__model')
    list_filter = ('product',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('model', 'quantity', 'source', 'destination')
    search_fields = ('model', 'source', 'destination')
    list_filter = ('source', 'destination')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch',)
    search_fields = ('branch',)


@admin.register(BranchProduct)
class BranchProductAdmin(admin.ModelAdmin):
    list_display = ('branch', 'product', 'quantity')
    search_fields = ('branch__branch', 'product__model')
    list_filter = ('branch', 'product')
