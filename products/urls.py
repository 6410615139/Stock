from django.urls import path
from . import views
from .views import ProductAutocomplete, BranchAutocomplete, SupplierAutocomplete

urlpatterns = [
    path('', views.view_product_list, name='view_product_list'),
    path('view_product_details/<int:id>', views.view_product_details, name='view_product_details'),
    path('add_product/', views.add_product, name='add_product'),
    path('update_product/<int:id>', views.update_product, name='update_product'),
    path('transactions/', views.view_transaction_list, name='view_transaction_list'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('view_import_list/', views.view_import_list, name='view_import_list'),
    path('import_product/', views.import_product, name='import_product'),
    path('view_branch_list/', views.view_branch_list, name='view_branch_list'),
    path('view_branch_details/<int:id>', views.view_branch_details, name='view_branch_details'),
    path('add_serial/', views.add_serial, name='add_serial'),
    path('view_serial_list/', views.view_serial_list, name='view_serial_list'),
    
    # auto complete
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
    path('branch-autocomplete/', BranchAutocomplete.as_view(), name='branch-autocomplete'),
    # path('supplier-autocomplete/', SupplierAutocomplete.as_view(), name='supplier-autocomplete'),
    
    # excel export
    path('export_to_excel/<str:instance>', views.export_to_excel, name='export_to_excel'),
]