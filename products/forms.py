from django import forms
# from dal import autocomplete
from dal_select2.widgets import ModelSelect2
from .models import Product, Transaction, Import, Serial

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['brand','model', 'description', 'EAN_code', 'dealer_price', 'volume_price', 'MSRP']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['product', 'quantity', 'source', 'destination']
        widgets = {
            'product': ModelSelect2(url='product-autocomplete'),
            'source': ModelSelect2(url='branch-autocomplete'),
            'destination': ModelSelect2(url='branch-autocomplete'),
        }

class ImportProductForm(forms.ModelForm):
    class Meta:
        model = Import
        fields = ['product', 'quantity']
        widgets = {
            'product': ModelSelect2(url='product-autocomplete'),
        }

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")

class SerialForm(forms.ModelForm):
    class Meta:
        model = Serial
        fields = ['serial', 'product']
        widgets = {
            'product': ModelSelect2(url='product-autocomplete')
        }

class MultipleSerialForm(forms.Form):
    model = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Product Model",
        widget=ModelSelect2(url='product-autocomplete')
    )
    serials = forms.CharField(
        label="Serials (space or enter separated)",
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "e.g. SN123 SN124\nSN125"}),
    )