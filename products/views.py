from django.shortcuts import render, redirect
from .models import Product
from django.contrib.auth.decorators import login_required, user_passes_test
import pandas as pd
from django.http import HttpResponse

def staff_check(user):
    return user.groups.filter(name='Staff').exists()

def admin_check(user):
    return user.is_superuser

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

from .forms import ProductForm

@user_passes_test(staff_check)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@user_passes_test(admin_check)
def export_to_excel(request):
    products = Product.objects.all()
    data = [{
        'Name': p.name,
        'Model': p.model,
        'Serial Number': p.serial_number,
        'Claim Active': p.is_claim_active(),
    } for p in products]

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="products.xlsx"'
    df.to_excel(response, index=False)
    return response
