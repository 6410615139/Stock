from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['image', 'name', 'model', 'serial_number', 'purchase_date', 'warranty_period']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),  # Render as a date input
        }

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")