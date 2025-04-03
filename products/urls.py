from django.urls import path
from . import views
from .views import ProductAutocomplete

urlpatterns = [
    path('', views.home, name='home'),
    path('add_product/', views.add_product, name='add_product'),
    path('add_serial/', views.add_serial, name='add_serial'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('export/', views.export_to_excel, name='export_to_excel'),
    path('branch/', views.branch, name='branch'),
    path('serial/', views.serial, name='serial'),
    path('product-autocomplete/', ProductAutocomplete.as_view(), name='product-autocomplete'),

]