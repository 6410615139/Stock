from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse

import pandas as pd
from .forms import ProductForm, UploadExcelForm, SerialForm, TransactionForm, MultipleSerialForm
from .models import (
    Product, Serial, SerialImportTransaction, Branch,
    BranchProduct, Transaction
)
from django.db.models import Sum

from dal import autocomplete

class BranchAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Branch.objects.none()
        qs = Branch.objects.all()
        if self.q:
            qs = qs.filter(branch__icontains=self.q)
        return qs

class ProductAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Product.objects.none()
        qs = Product.objects.all()
        if self.q:
            qs = qs.filter(model__icontains=self.q)
        return qs
    
def admin_check(user):
    return user.is_superuser

@login_required
def home(request):
    products = Product.objects.all()

    # default query
    default = request.GET.get('default', "")
    if default != "":
        products = products.filter(
            Q(brand__icontains=default) | 
            Q(model__icontains=default) |
            Q(EAN_code__icontains=default)
        )

    # selected column setting
    selected_columns = request.GET.getlist('columns')
    if not selected_columns:
        selected_columns = ['brand','model', 'description', 'EAN_code', 'dealer_price', 'volumn_price', 'MSRP', "total"]

    # searchbar query
    query = request.GET.get('q')  # Get the search query from the request
    if query:
        products = products.filter(
            Q(brand__icontains=query) | 
            Q(model__icontains=query) |
            Q(EAN_code__icontains=query)
        )

    for product in products:
        product.total_quantity = sum(
            item.quantity for item in product.branchproduct_set.all()
        )

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

    serials = Serial.objects.all()
    
    query = request.GET.get('q')  # Get the search query from the request
    if query:
        serials = Serial.objects.filter(
            Q(serial__icontains=query)
        )
    default = request.GET.get('default')
    if default is None:
        default=""
    model_name = request.GET.get('model')
    viewModel = {
        'default': default,
        'serials': serials,
        'query': query
    }

    return render(request, 'serial.html', viewModel)

@login_required
def add_serial(request):
    if request.method == 'POST':
        submit_type = request.POST.get('submit_type')

        # ✅ Excel Upload
        if submit_type == 'excel' and 'excel_file' in request.FILES:
            excel_form = UploadExcelForm(request.POST, request.FILES)
            if excel_form.is_valid():
                excel_file = request.FILES['excel_file']
                df = pd.read_excel(excel_file)

                model_counter = {}

                for _, row in df.iterrows():
                    serial_number = row.get('Serial Number')
                    model_name = row.get('Model')

                    try:
                        product = Product.objects.get(model=model_name)
                        Serial.objects.create(serial=serial_number, product=product)
                        model_counter[model_name] = model_counter.get(model_name, 0) + 1
                    except Product.DoesNotExist:
                        continue

                _process_import_transaction(model_counter, request.user)
                return redirect('serial')

        # ✅ Multiple serials via textarea
        elif submit_type == 'multiple':
            multiple_serial_form = MultipleSerialForm(request.POST)
            if multiple_serial_form.is_valid():
                serials_input = multiple_serial_form.cleaned_data['serials']
                model_name = multiple_serial_form.cleaned_data['model']
                model_counter = {}

                try:
                    product = Product.objects.get(model=model_name)
                    serials = serials_input.replace('\r', '').split('\n')
                    count = 0
                    for s in serials:
                        for serial in s.split():
                            Serial.objects.create(serial=serial.strip(), product=product)
                            count += 1
                    model_counter[model_name] = count
                except Product.DoesNotExist:
                    print(f"❌ Product model '{model_name}' not found")

                _process_import_transaction(model_counter, request.user)
                return redirect('serial')

        # ✅ Single serial input
        elif submit_type == 'single':
            form = SerialForm(request.POST)
            if form.is_valid():
                serial = form.save()
                model_name = serial.product.model
                _process_import_transaction({model_name: 1}, request.user)
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

# ✅ Helper function to create transaction records and update stock
def _process_import_transaction(model_counter, user):
    hq_branch, _ = Branch.objects.get_or_create(branch="HQ")

    for model_name, quantity in model_counter.items():
        try:
            product = Product.objects.get(model=model_name)

            # Create SerialImportTransaction
            SerialImportTransaction.objects.create(
                imported_by=user,
                model=product,
                quantity=quantity
            )

            # Update HQ stock
            branch_product, _ = BranchProduct.objects.get_or_create(
                branch=hq_branch,
                product=product,
                defaults={'quantity': 0}
            )
            branch_product.quantity += quantity
            branch_product.save()

        except Product.DoesNotExist:
            continue

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)

            product_model = transaction.model  # this is a Product instance if you changed to ForeignKey
            quantity = transaction.quantity
            source_branch = transaction.source
            destination_branch = transaction.destination

            # Get source stock
            source_stock = BranchProduct.objects.filter(branch=source_branch, product=product_model).first()
            if not source_stock or source_stock.quantity < quantity:
                form.add_error('quantity', f"Not enough stock in {source_branch}. Available: {source_stock.quantity if source_stock else 0}")
                return render(request, 'add_transaction.html', {'form': form})

            # ✅ Subtract from source
            source_stock.quantity -= quantity
            source_stock.save()

            # ✅ Add to destination (get or create)
            dest_stock, _ = BranchProduct.objects.get_or_create(
                branch=destination_branch,
                product=product_model,
                defaults={'quantity': 0}
            )
            dest_stock.quantity += quantity
            dest_stock.save()

            transaction.imported_by = request.user
            transaction.save()

            return redirect('branch_details', id=destination_branch.id)
    else:
        form = TransactionForm()

    return render(request, 'add_transaction.html', {'form': form})