from django.contrib import admin
from .models import Product, Serial, Branch, SerialImportTransaction, Transaction, BranchProduct


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'EAN_code', 'dealer_price', 'volumn_price', 'MSRP')
    search_fields = ('brand', 'model', 'EAN_code')


@admin.register(Serial)
class SerialAdmin(admin.ModelAdmin):
    list_display = ('serial', 'product')
    search_fields = ('serial',)
    list_filter = ('product',)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch',)
    search_fields = ('branch',)


@admin.register(SerialImportTransaction)
class SerialImportTransactionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'imported_by', 'product', 'quantity')
    list_filter = ('created_at', 'imported_by', 'product')
    search_fields = ('product__model', 'imported_by__username')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'imported_by', 'product', 'quantity', 'source', 'destination')
    list_filter = ('created_at', 'imported_by', 'product', 'source', 'destination')
    search_fields = ('product__model', 'imported_by__username')


@admin.register(BranchProduct)
class BranchProductAdmin(admin.ModelAdmin):
    list_display = ('branch', 'product_model', 'quantity')
    list_filter = ('branch', 'product')  # ← only direct ForeignKeys allowed
    search_fields = ('branch__branch', 'product__model')

    def product_model(self, obj):
        return obj.product.model
    product_model.short_description = 'Product Model'



