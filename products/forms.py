from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['image', 'name', 'model', 'serial_number', 'purchase_date', 'warranty_period']
