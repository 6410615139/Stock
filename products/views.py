from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # Import Paginator

import pandas as pd
from .forms import (
    ProductForm, UploadExcelForm, TransactionForm, ImportProductForm,
    SerialForm, MultipleSerialForm
)
from .models import (
    Product, Branch, Serial,
    BranchProduct, Transaction, Import, Supplier
)
from urllib.parse import urlencode
from django.utils.timezone import now
from dal import autocomplete

from django.utils.text import slugify

class BranchAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Branch.objects.none()
        qs = Branch.objects.all()
        if self.q:
            qs = qs.filter(branch__icontains=self.q)
        return qs
    
class SupplierAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Supplier.objects.none()
        qs = Supplier.objects.all()
        if self.q:
            qs = qs.filter(supplier__icontains=self.q)
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
def view_product_list(request):
    products = Product.objects.all()

    # default query
    default = request.GET.get('default', "")
    if default != "":
        products = products.filter(
            Q(brand__icontains=default) | 
            Q(model__icontains=default) |
            Q(EAN_code__icontains=default)
        )

    available_columns = [
        ("brand", "Brand"),
        ("model", "Model"),
        ("description", "Description"),
        ("EAN_code", "EAN code"),
        ("dealer_price", "Dealer Price"),
        ("volume_price", "volume Price"),
        ("MSRP", "MSRP"),
        ("total", "Total"),
    ]

    # selected column setting
    selected_columns = request.GET.getlist('columns')
    if not selected_columns:
        selected_columns = ['brand','model', 'description', 'EAN_code', 'dealer_price', 'volume_price', 'MSRP', "total"]

    # searchbar query
    query = request.GET.get('q')  # Get the search query from the request
    if query:
        products = products.filter(
            Q(brand__icontains=query) | 
            Q(model__icontains=query) |
            Q(EAN_code__icontains=query)
        )

    # --- Pagination Implementation ---
    paginator = Paginator(products, 30)  # Show 30 products per page
    page = request.GET.get('page')
    # Exclude 'page' from query params
    query_params = request.GET.copy()
    query_params.pop('page', None)
    base_query = query_params.urlencode()


    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products_page = paginator.page(paginator.num_pages)
    # --- End Pagination Implementation ---

    viewModel = {
        "base_query": base_query,
        'default': default,
        'products': products_page,  # Use the paginated queryset here
        'query': query, 
        'selected_columns': selected_columns,
        "available_columns": available_columns
    }
    
    return render(request, 'view_product_list.html', viewModel)

@login_required
def view_product_details(request, id):
    product = get_object_or_404(Product, id=id)

    branch_q = request.GET.get("branch_q")
    txn_q = request.GET.get("txn_q")

    branches = product.branchproduct_set.select_related("branch")
    if branch_q:
        branches = branches.filter(branch__branch__icontains=branch_q)

    transactions = Transaction.objects.filter(product=product).select_related("source", "destination", "imported_by")
    if txn_q:
        transactions = transactions.filter(
            Q(source__branch__icontains=txn_q) | 
            Q(destination__branch__icontains=txn_q) |
            Q(imported_by__username__icontains=txn_q)
        )

    return render(request, "view_product_details.html", {
        "product": product,
        "branch_q": branch_q,
        "txn_q": txn_q,
        "branches": branches,
        "transactions": transactions,
    })

@login_required
def add_product(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            excel_form = UploadExcelForm(request.POST, request.FILES)
            form = ProductForm()  # re-render in case Excel form is invalid

            if excel_form.is_valid():
                excel_file = request.FILES['excel_file']
                df = pd.read_excel(excel_file)

                for _, row in df.iterrows():
                    try:
                        # Gracefully handle missing values
                        Product.objects.create(
                            brand=row.get('Brand', ''),
                            model=row.get('Model', ''),
                            description=row.get('Description', ''),
                            EAN_code=row.get('EAN Code', ''),
                            dealer_price=float(row.get('Dealer Price', 0)),
                            volume_price=float(row.get('Volume Price', 0)),
                            MSRP=float(row.get('MSRP', 0)),
                        )
                    except Exception as e:
                        print(f"Error creating product from row: {row} -> {e}")
                        continue

                return redirect('view_product_list')
        else:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('view_product_list')
    else:
        form = ProductForm()
        excel_form = UploadExcelForm()

    viewModel = {
        'form': form, 
        'excel_form': excel_form
    }

    return render(request, 'add_product.html', viewModel)

@login_required
def update_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('view_product_details', id=id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'update_product.html', {'form': form, 'product': product})


@login_required
def view_branch_list(request):
    branches = Branch.objects.all()
    viewModel = {
        'branches': branches,
    }
    return render(request, 'view_branch_list.html', viewModel)

@login_required
def view_branch_details(request, id):
    branch = get_object_or_404(Branch, id=id)

    product_q = request.GET.get("product_q", "")
    txn_q = request.GET.get("txn_q", "")

    products = BranchProduct.objects.select_related("product").filter(branch=branch)
    if product_q:
        products = products.filter(
            Q(product__brand__icontains=product_q) |
            Q(product__model__icontains=product_q) |
            Q(product__description__icontains=product_q) |
            Q(quantity__icontains=product_q)
        )

    transactions = Transaction.objects.select_related("product", "imported_by", "source", "destination").filter(
        Q(source=branch) | Q(destination=branch)
    )
    if txn_q:
        transactions = transactions.filter(
            Q(product__model__icontains=txn_q) |
            Q(imported_by__username__icontains=txn_q)
        )

    # --- Pagination Implementation ---
    products_paginator = Paginator(products, 10)
    page = request.GET.get('page')
    # Exclude 'page' from query params
    query_params = request.GET.copy()
    query_params.pop('page', None)
    products_base_query = query_params.urlencode()


    try:
        products_page = products_paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products_page = products_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products_page = products_paginator.page(products_paginator.num_pages)
    # --- End Pagination Implementation ---

    # --- Pagination Implementation ---
    transactions_paginator = Paginator(transactions, 10)
    page = request.GET.get('page')
    # Exclude 'page' from query params
    query_params = request.GET.copy()
    query_params.pop('page', None)
    transations_base_query = query_params.urlencode()


    try:
        transations_page = transactions_paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transations_page = transactions_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transations_page = transactions_paginator.page(transactions_paginator.num_pages)
    # --- End Pagination Implementation ---

    viewModel = {
        "products_base_query": products_base_query,
        "transations_base_query": transations_base_query,
        "branch": branch,
        "product_q": product_q,
        "txn_q": txn_q,
        "products": products_page,
        "transactions": transations_page,
    }

    return render(request, "view_branch_details.html", viewModel)

@login_required
def view_serial_list(request):

    serials = Serial.objects.all()
    
    query = request.GET.get('q')
    if query:
        serials = Serial.objects.filter(
            Q(serial__icontains=query)
        )
    default = request.GET.get('default')
    if default is None:
        default=""

    viewModel = {
        'default': default,
        'serials': serials,
        'query': query
    }

    return render(request, 'view_serial_list.html', viewModel)

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
                    serial_number = str(row.get('Serial')).strip()
                    model_name = row.get('Model')

                    if not serial_number or not model_name:
                        continue

                    try:
                        product = Product.objects.get(model=model_name)
                        if Serial.objects.filter(serial=serial_number).exists():
                            continue
                        Serial.objects.create(serial=serial_number, product=product)
                        model_counter[model_name] = model_counter.get(model_name, 0) + 1
                    except Product.DoesNotExist:
                        continue

                # _process_import_transaction(model_counter, request.user)
                return redirect('view_serial_list')

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

                # _process_import_transaction(model_counter, request.user)
                return redirect('view_serial_list')

        # ✅ Single serial input
        elif submit_type == 'single':
            form = SerialForm(request.POST)
            if form.is_valid():
                serial = form.save()
                model_name = serial.product.model
                # _process_import_transaction({model_name: 1}, request.user)
                return redirect('view_serial_list')

    else:
        form = SerialForm()
        excel_form = UploadExcelForm()
        multiple_serial_form = MultipleSerialForm()

    return render(request, 'add_serial.html', {
        'single_serial_form': form,
        'excel_form': excel_form,
        'multiple_serial_form': multiple_serial_form,
    })

# # ✅ Helper function to create transaction records and update stock
# def _process_import_transaction(model_counter, user):
#     hq_branch, _ = Branch.objects.get_or_create(branch="สำนักงานใหญ่")

#     for model_name, quantity in model_counter.items():
#         try:
#             product = Product.objects.get(model=model_name)

#             # Create SerialImportTransaction
#             SerialImportTransaction.objects.create(
#                 imported_by=user,
#                 product=product,
#                 quantity=quantity
#             )

#             # Update HQ stock
#             branch_product, _ = BranchProduct.objects.get_or_create(
#                 branch=hq_branch,
#                 product=product,
#                 defaults={'quantity': 0}
#             )
#             branch_product.quantity += quantity
#             branch_product.save()

#         except Product.DoesNotExist:
#             continue

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)

            product = transaction.product
            quantity = transaction.quantity
            source_branch = transaction.source
            destination_branch = transaction.destination

            # Get source stock
            source_stock = BranchProduct.objects.filter(branch=source_branch, product=product).first()
            if not source_stock or source_stock.quantity < quantity:
                form.add_error('quantity', f"Not enough stock in {source_branch}. Available: {source_stock.quantity if source_stock else 0}")
                return render(request, 'add_transaction.html', {'form': form})

            # ✅ Subtract from source
            source_stock.quantity -= quantity
            source_stock.save()

            # ✅ Add to destination (get or create)
            dest_stock, _ = BranchProduct.objects.get_or_create(
                branch=destination_branch,
                product=product,
                defaults={'quantity': 0}
            )
            dest_stock.quantity += quantity
            dest_stock.save()

            transaction.imported_by = request.user
            transaction.save()

            return redirect('view_branch_details', id=destination_branch.id)
    else:
        form = TransactionForm()

    return render(request, 'add_transaction.html', {'form': form})

@login_required
@user_passes_test(admin_check)
def import_product(request):
    if request.method == 'POST':
            if 'excel_file' in request.FILES:
                excel_form = UploadExcelForm(request.POST, request.FILES)
                form = ImportProductForm(request.POST, request.FILES)

                if excel_form.is_valid():
                    excel_file = request.FILES['excel_file']
                    df = pd.read_excel(excel_file)

                    for _, row in df.iterrows():
                        try:
                            product = Product.objects.create(
                                brand=row.get('Brand', ''),
                                model=row.get('Model', ''),
                                description=row.get('Description', ''),
                                EAN_code=row.get('EAN Code', ''),
                                dealer_price=float(row.get('Dealer Price', 0)),
                                volume_price=float(row.get('Volume Price', 0)),
                                MSRP=float(row.get('MSRP', 0)),
                            )
                            supplier = Supplier.objects.get(name="อื่นๆ")
                            import_product = Import.objects.create(
                                product=product,
                                imported_by = request.user,
                                quantity=row.get('Total', ''),
                                supplier=supplier
                            )
                            import_product.create_branch_product()
                            import_product.save()

                        except Exception as e:
                            print(f"Error creating product from row: {row} -> {e}")
                            continue

                    return redirect('view_import_list')
            
            else:
                form = ImportProductForm(request.POST, request.FILES)
                if form.is_valid():
                    import_product = form.save(commit=False)
                    import_product.imported_by = request.user
                    import_product.save()

                    import_product.create_branch_product()
                    return redirect('view_import_list')

    else:
        form = ImportProductForm()
        excel_form = UploadExcelForm()

    viewModel = {
        'form': form, 
        'excel_form': excel_form
    }
        
    return render(request, 'import_product.html', viewModel)

def view_import_list(request):
    imports = Import.objects.select_related("product", "imported_by")

    # default query
    default = request.GET.get('default', "")
    if default != "":
        imports = imports.filter(
            Q(created_at__icontains=default) | 
            Q(imported_by__username__icontains=default) | 
            Q(product__model__icontains=default) |
            Q(quantity__icontains=default)
        )

    # searchbar query
    query = request.GET.get('q')  # Get the search query from the request
    if query:
        imports = imports.filter(
            Q(created_at__icontains=query) | 
            Q(imported_by__username__icontains=query) | 
            Q(product__model__icontains=query) |
            Q(quantity__icontains=query)
        )

    # --- Pagination Implementation ---
    paginator = Paginator(imports, 30)
    page = request.GET.get('page')
    # Exclude 'page' from query params
    query_params = request.GET.copy()
    query_params.pop('page', None)
    base_query = query_params.urlencode()


    try:
        imports_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        imports_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        imports_page = paginator.page(paginator.num_pages)
    # --- End Pagination Implementation ---

    viewModel = {
        'default': default,
        "base_query": base_query,
        "imports": imports_page,
    }
    return render(request, "view_import_list.html", viewModel)

@login_required
def export_to_excel(request, instance):
    model_map = {
        "products": Product,
        "branches": Branch,
        "serials": Serial,
        "branchproducts": BranchProduct,
        "transactions": Transaction,
        "imports": Import,
        # "suppliers": Supplier
    }

    model = model_map.get(instance)
    if not model:
        raise Http404("Invalid export type")

    filters = request.GET.dict()
    queryset = model.objects.filter(**filters)

    # Add select_related() for performance based on model
    if instance == "serials":
        queryset = queryset.select_related("product")
    elif instance == "branchproducts":
        queryset = queryset.select_related("branch", "product")
    elif instance == "transactions":
        queryset = queryset.select_related("product", "source", "destination", "imported_by")

    data = [obj.to_excel_row() for obj in queryset]
    df = pd.DataFrame(data)

    # Filename suffix: model and/or branch for branchproducts or transactions
    suffix_parts = []
    if instance in ["branchproducts", "transactions"]:
        model_name = request.GET.get("model__model")
        source_branch = request.GET.get("source__branch")
        destination_branch = request.GET.get("destination__branch")
        if model_name:
            suffix_parts.append(slugify(model_name))
        if source_branch:
            suffix_parts.append("from-" + slugify(source_branch))
        if destination_branch:
            suffix_parts.append("to-" + slugify(destination_branch))

    suffix = "-" + "-".join(suffix_parts) if suffix_parts else ""

    filename = f"{now().strftime('%Y-%m-%d')}-{instance}{suffix}.xlsx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    df.to_excel(response, index=False)
    return response

@login_required
def view_transaction_list(request):
    query = request.GET.get("q")
    transactions = Transaction.objects.select_related("product", "source", "destination", "imported_by")

    if query:
        transactions = transactions.filter(product__model__icontains=query)

    transactions = transactions.order_by("-created_at")

    # --- Pagination Implementation ---
    paginator = Paginator(transactions, 30)  # Show 30 products per page
    page = request.GET.get('page')
    # Exclude 'page' from query params
    query_params = request.GET.copy()
    query_params.pop('page', None)
    base_query = query_params.urlencode()


    try:
        transactions_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions_page = paginator.page(paginator.num_pages)
    # --- End Pagination Implementation ---

    viewModel = {
        "base_query": base_query,
        "transactions": transactions_page,
        "query": query,
    }

    return render(request, "view_transaction_list.html", viewModel)