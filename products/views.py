from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse

import pandas as pd
from .forms import ProductForm, UploadExcelForm, SerialForm, TransactionForm, MultipleSerialForm
from .models import Product, Serial, BranchProduct, Branch
from django.db.models import Sum

from dal_select2.views import Select2QuerySetView

class ProductAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Product.objects.all()
        if self.q:
            qs = qs.filter(
                Q(model__icontains=self.q) |
                Q(brand__icontains=self.q) |
                Q(EAN_code__icontains=self.q)
            )
        return qs


def admin_check(user):
    return user.is_superuser

@login_required
def home(request):
    default = request.GET.get('default')
    if default is None:
        default=""
    # Get selected columns from the query string
    selected_columns = request.GET.getlist('columns')
    if not selected_columns:
        selected_columns = ['brand','model', 'description', 'EAN_code', 'dealer_price', 'volumn_price', 'MSRP', "total"]  # Default columns

    query = request.GET.get('q')  # Get the search query from the request
    if query:
        products = Product.objects.filter(
            Q(brand__icontains=query) | 
            Q(model__icontains=query) |
            Q(EAN_code__icontains=query)
        )

    else:
        products = Product.objects.all()  # Show all products if no search query
    viewModel = {
        'default': default,
        'products': products, 
        'query': query, 
        'selected_columns': selected_columns
        }
    return render(request, 'home.html', viewModel)

def product_details(request, id):
    product = Product.objects.get(id=id)
    viewModel = {
        'product': product,
    }
    return render(request, 'product_details.html', viewModel)

@user_passes_test(admin_check)
def add_product(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            excel_form = UploadExcelForm(request.POST, request.FILES)
            if excel_form.is_valid():
                excel_file = request.FILES['excel_file']
                df = pd.read_excel(excel_file)

                # Convert DataFrame to Products
                for _, row in df.iterrows():
                    warranty_period = row.get('Warranty Period (months)', 0)
                    if not (0 <= warranty_period <= 120):  # Validate warranty period
                        raise ValueError(f"Invalid warranty period: {warranty_period}")
                    
                    Product.objects.create(
                        name=row['Name'],
                        model=row['Model'],
                        serial_number=row['Serial Number'],
                        purchase_date=pd.to_datetime(row['Purchase Date']).date(),
                        warranty_period=int(warranty_period),
                        image=row.get('Image', None),
                    )
                return redirect('home')
        else:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('home')
    else:
        form = ProductForm()
        excel_form = UploadExcelForm()

    viewModel = {
        'form': form, 
        'excel_form': excel_form
    }

    return render(request, 'add_product.html', viewModel)

@login_required
def export_to_excel(request):
    # Fetch all products
    products = Product.objects.all()

    # Prepare data for export
    data = [
        {
            'Timestamp': p.tstamp.strftime('%Y-%m-%d %H:%M'),
            'Image': p.image.url if p.image else None,
            'Serial Number': p.serial_number,
            'Name': p.name,
            'Model': p.model,
            'Purchase Date': p.purchase_date.strftime('%Y-%m-%d'),
            'Warranty Period (months)': p.warranty_period,
            'Claim Active': 'Yes' if p.is_claim_active() else 'No',
        }
        for p in products
    ]

    # Create DataFrame
    df = pd.DataFrame(data)

    # Create HTTP response with Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

    # Export DataFrame to Excel
    df.to_excel(response, index=False)
    return response

@login_required
def branches(request):
    branches = Branch.objects.all()
    viewModel = {
        'branches': branches,
    }
    return render(request, 'branches.html', viewModel)

@login_required
def branch_details(request, id):
    branch = get_object_or_404(Branch, id=id)
    products = BranchProduct.objects.filter(branch=branch)

    viewModel = {
        'branch': branch,
        'products': products,
    }

    return render(request, 'branch_details.html', viewModel)

# @login_required
# def branch(request):
#     default = request.GET.get('default')
#     if default is None:
#         default=""
#     model_name = request.GET.get('q')

#     if model_name is None:
#         model_name = ""
    
#     branches = (BranchProduct.objects
#             .filter(product__model__icontains=model_name)
#             .values('branch__branch')
#             .annotate(total_quantity=Sum('quantity'))
#             .order_by('branch__branch'))

#     print(branches)

#     viewModel = {
#         'default': default,
#         'branches': branches,
#     }

#     return render(request, 'productBranch.html', viewModel)

@login_required
def serial(request):
    default = request.GET.get('default')
    if default is None:
        default=""
    model_name = request.GET.get('model')
    
    # Get grouped branch data
    serials = Serial.objects.all()

    viewModel = {
        'default': default,
        'serials': serials,
    }

    return render(request, 'serial.html', viewModel)

@login_required
def add_serial(request):
    if request.method == 'POST':
        submit_type = request.POST.get('submit_type')

        # Excel upload
        if submit_type == 'excel' and 'excel_file' in request.FILES:
            excel_form = UploadExcelForm(request.POST, request.FILES)
            if excel_form.is_valid():
                excel_file = request.FILES['excel_file']
                df = pd.read_excel(excel_file)

                for _, row in df.iterrows():
                    serial_number = row.get('Serial Number')
                    model_name = row.get('Model')

                    try:
                        product = Product.objects.get(model=model_name)
                        Serial.objects.create(
                            serial=serial_number,
                            product=product
                        )
                    except Product.DoesNotExist:
                        continue

                return redirect('serial')

        # Multiple serials (textarea input)
        elif submit_type == 'multiple':
            multiple_serial_form = MultipleSerialForm(request.POST)
            if multiple_serial_form.is_valid():
                serials_input = multiple_serial_form.cleaned_data['serials']
                model_name = multiple_serial_form.cleaned_data['model']

                try:
                    product = Product.objects.get(model=model_name)
                    print(f"✅ Found product: {product}")
                    serials = serials_input.replace('\r', '').split('\n')
                    for s in serials:
                        for serial in s.split():  # split by space
                            Serial.objects.create(serial=serial.strip(), product=product)
                except Product.DoesNotExist:
                    print(f"❌ Product model '{model_name}' not found")

                return redirect('serial')

        # Single serial
        elif submit_type == 'single':
            form = SerialForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('serial')

    else:
        form = SerialForm()
        excel_form = UploadExcelForm()
        multiple_serial_form = MultipleSerialForm()

    return render(request, 'add_serial.html', {
        'single_serial_form': form,
        'excel_form': excel_form,
        'multiple_serial_form': multiple_serial_form,
    })

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('serial')
    else:
        form = TransactionForm()

    viewModel = {
        'form': form, 
    }

    return render(request, 'add_transaction.html', viewModel)
