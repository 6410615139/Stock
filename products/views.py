from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse

import pandas as pd
from .forms import ProductForm, UploadExcelForm, ProductHistoryForm
from .models import Product, ProductHistory

def admin_check(user):
    return user.is_superuser

@login_required
def home(request):
    # Get selected columns from the query string
    selected_columns = request.GET.getlist('columns')
    if not selected_columns:
        selected_columns = ['timestamp', 'serial_number', 'image', 'name', 'model', 'claim_active']  # Default columns

    query = request.GET.get('q')  # Get the search query from the request
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(model__icontains=query) |
            Q(serial_number__icontains=query)
        )

    else:
        products = Product.objects.all()  # Show all products if no search query
    viewModel = {
        'products': products, 
        'query': query, 
        'selected_columns': selected_columns
        }
    return render(request, 'home.html', viewModel)

@login_required
def add_product(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            excel_form = UploadExcelForm(request.POST, request.FILES)
            if excel_form.is_valid():
                excel_file = request.FILES['excel_file']
                df = pd.read_excel(excel_file)

                # Convert DataFrame to Products
                for _, row in df.iterrows():
                    Product.objects.create(
                        name=row['Name'],
                        model=row['Model'],
                        serial_number=row['Serial Number'],
                        purchase_date=pd.to_datetime(row['Purchase Date']).date(),  # Ensure DateField
                        warranty_period=int(row['Warranty Period (months)']),
                        image=row.get('Image', None),  # Optional image
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

@user_passes_test(admin_check)
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

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product_histories = ProductHistory.objects.filter(product=product).order_by('-timestamp')
    warranty_days_left = product.warranty_days_left()

    return render(request, 'product_detail.html', {
        'product': product,
        'warranty_days_left': warranty_days_left,
        'product_histories': product_histories,
    })

@login_required
def product_report(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductHistoryForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.product = product  # Associate the report with the product
            report.save()
            return redirect('product_detail', pk=product.pk)  # Redirect to the product detail page
    else:
        form = ProductHistoryForm(initial={'product': product})  # Pre-fill the product

    return render(request, 'product_report.html', {'form': form, 'product': product})