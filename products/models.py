from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    EAN_code = models.CharField(max_length=20)
    dealer_price = models.FloatField()
    volume_price = models.FloatField()
    MSRP = models.FloatField()

    def __str__(self):
        return self.model
    
    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.branchproduct_set.all())
    
    def to_excel_row(self):
        return {
            "Brand": self.brand,
            "Model": self.model,
            "Description": self.description,
            "EAN Code": self.EAN_code,
            "Dealer Price": self.dealer_price,
            "Volume Price": self.volume_price,
            "MSRP": self.MSRP,
            "Total": self.total_quantity,
        }


class Serial(models.Model):
    serial = models.CharField(max_length=30, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='serials')

    def __str__(self):
        return f"{self.serial} - {self.product.model}"
    
    def to_excel_row(self):
        return {
            "Serial": self.serial,
            "Product Model": self.product.model,
            "Product Brand": self.product.brand,
        }

class Branch(models.Model):
    branch = models.CharField(max_length=30)
    # details = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.branch
    
    def to_excel_row(self):
        return {
            "Branch Name": self.branch,
            # "Details": self.details if self.details else "",
        }
    
class SerialImportTransaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()

    def to_excel_row(self):
        return {
            "Created At": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "Imported By": self.imported_by.username if self.imported_by else "Unknown",
            "Model": self.product.model,
            "Quantity": self.quantity,
        }

class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    source = models.ForeignKey(Branch, on_delete=models.PROTECT, null=False, blank=False, related_name='source')
    destination = models.ForeignKey(Branch, on_delete=models.PROTECT, null=False, blank=False, related_name='destination')

    def __str__(self):
        return f"Transaction of {self.quantity} {self.model} from {self.source} to {self.destination}"

    def to_excel_row(self):
        return {
            "Created At": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "Imported By": self.imported_by.username if self.imported_by else "Unknown",
            "Model": self.product.model,
            "Quantity": self.quantity,
            "Source Branch": self.source.branch,
            "Destination Branch": self.destination.branch,
        }
    
class BranchProduct(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.branch.branch} - {self.product.model} ({self.quantity})"

    def to_excel_row(self):
        return {
            "Branch": self.branch.branch,
            "Product Model": self.product.model,
            "Quantity": self.quantity,
        }