from django.urls import path
from . import views
from .views import ProductAutocomplete, BranchAutocomplete  

urlpatterns = [
    path('', views.view_product_list, name='view_product_list'),
    path('view_product_details/<int:id>', views.view_product_details, name='view_product_details'),
    path('add_product/', views.add_product, name='add_product'),
    path('add_serial/', views.add_serial, name='add_serial'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('view_branch_list/', views.view_branch_list, name='view_branch_list'),
    path('view_branch_details/<int:id>', views.view_branch_details, name='view_branch_details'),
    path('view_serial_list/', views.view_serial_list, name='view_serial_list'),
    
    # auto complete
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),
    path('branch-autocomplete/', BranchAutocomplete.as_view(), name='branch-autocomplete'),
    
    # excel export
    path('export_to_excel/<str:instance>', views.export_to_excel, name='export_to_excel'),

]