from django.urls import path
from . import views
from .views import ProductAutocomplete, BranchAutocomplete  

urlpatterns = [
    path('', views.home, name='home'),
    path('product_details/<int:id>', views.product_details, name='product_details'),
    path('add_product/', views.add_product, name='add_product'),
    path('add_serial/', views.add_serial, name='add_serial'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('branches/', views.branches, name='branches'),
    path('branch_details/<int:id>', views.branch_details, name='branch_details'),
    path('serial/', views.serial, name='serial'),
    
    # auto complete
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
    path('branch-autocomplete/', BranchAutocomplete.as_view(), name='branch-autocomplete'),
    
    # excel export
    path('export_to_excel/<str:instance>', views.export_to_excel, name='export_to_excel'),

]