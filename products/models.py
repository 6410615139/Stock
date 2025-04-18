from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    EAN_code = models.CharField(max_length=20)
    dealer_price = models.FloatField()
    volumn_price = models.FloatField()
    MSRP = models.FloatField()

    def __str__(self):
        return self.model


class Serial(models.Model):
    serial = models.CharField(max_length=30, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='serials')

    def __str__(self):
        return f"{self.serial} - {self.product.model}"

class Branch(models.Model):
    branch = models.CharField(max_length=30)
    # details = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.branch
    
class SerialImportTransaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    model = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()    

class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    model = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    source = models.ForeignKey(Branch, on_delete=models.PROTECT, null=False, blank=False, related_name='source')
    destination = models.ForeignKey(Branch, on_delete=models.PROTECT, null=False, blank=False, related_name='destination')

    def __str__(self):
        return f"Transaction of {self.quantity} {self.model} from {self.source} to {self.destination}"

class BranchProduct(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='products')
    model = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.branch.branch} - {self.product.model} ({self.quantity})"
