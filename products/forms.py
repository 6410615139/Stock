from django import forms
from .models import Product, ProductHistory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['image', 'name', 'model', 'serial_number', 'purchase_date', 'warranty_period']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),  # Render as a date input
        }

    warranty_period = forms.CharField(required=False, label="Warranty Period", help_text="Enter 'Forever' or a number of months.")

    def clean_warranty_period(self):
        warranty_period = self.cleaned_data.get('warranty_period')
        if warranty_period is None or warranty_period.strip().lower() == "forever":
            return None  # Represent "Forever" as None
        try:
            warranty_period = int(warranty_period)
            if warranty_period < 0:
                raise forms.ValidationError("Warranty period cannot be negative.")
        except ValueError:
            raise forms.ValidationError("Please enter 'Forever' or a valid number.")
        return warranty_period

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")

class ProductHistoryForm(forms.ModelForm):
    class Meta:
        model = ProductHistory
        fields = ['product', 'details', 'claim_active']