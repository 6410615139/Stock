from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_product, name='add_product'),
    path('export/', views.export_to_excel, name='export_to_excel'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]