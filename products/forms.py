from django import forms
from dal import autocomplete
from dal_select2.widgets import ModelSelect2
from .models import Product, Serial, Transaction

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['brand','model', 'description', 'EAN_code', 'dealer_price', 'volumn_price', 'MSRP']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['model', 'quantity', 'source', 'destination']

class SerialForm(forms.ModelForm):
    class Meta:
        model = Serial
        fields = ['serial', 'product']
        # widgets = {
        #     'product': ModelSelect2(url='product-autocomplete')
        # }

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")