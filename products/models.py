from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    brand = models.CharField(max_length=20, null=True, blank=True)
    model = models.CharField(max_length=30, null=False, blank=False, unique=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    EAN_code = models.CharField(max_length=20, null=True, blank=True)
    dealer_price = models.FloatField(null=True, blank=True)
    volume_price = models.FloatField(null=True, blank=True)
    MSRP = models.FloatField(null=True, blank=True)

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

class Branch(models.Model):
    name = models.CharField(max_length=30)
    details = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def to_excel_row(self):
        return {
            "Name": self.name,
            "Details": self.details if self.details else "",
        }

class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    source = models.ForeignKey(Branch, on_delete=models.PROTECT, null=False, blank=False, related_name='source')
    destination = models.ForeignKey(Branch, on_delete=models.PROTECT, null=False, blank=False, related_name='destination')
    invoice = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Transaction of {self.quantity} {self.product.model} from {self.source} to {self.destination}"

    def to_excel_row(self):
        return {
            "Created At": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "Imported By": self.imported_by.username if self.imported_by else "Unknown",
            "Model": self.product.model,
            "Quantity": self.quantity,
            "Source Branch": self.source,
            "Destination Branch": self.destination,
        }
    
class Supplier(models.Model):
    name = models.CharField(max_length=30)
    details = models.CharField(max_length=300, null=True, blank=True)
    total = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def to_excel_row(self):
        return {
            "Name": self.name,
            "Details": self.details if self.details else "",
        }
    
class Import(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    imported_by = models.ForeignKey(User, on_delete=models.PROTECT, null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='suplier', null=False, blank=False)

    def __str__(self):
        return f"Importing of {self.quantity} {self.model} from {self.suplier}"

    def to_excel_row(self):
        return {
            "Created At": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "Imported By": self.imported_by.username if self.imported_by else "Unknown",
            "Model": self.product.model,
            "Quantity": self.quantity,
            "Supplier": self.supplier,
        }
    
    def create_branch_product(self):
        branch = Branch.objects.get(name='สำนักงานใหญ่')
        branchProduct, created = BranchProduct.objects.get_or_create(
            branch=branch,
            product=self.product # self.product is already the Product instance linked to this Import
        )
        branchProduct.quantity += self.quantity # Use the quantity from the current Import instance
        branchProduct.save()
        supplier = self.supplier
        supplier.total += self.quantity
        supplier.save()

class BranchProduct(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return f"{self.branch.name} - {self.product.model} ({self.quantity})"

    def to_excel_row(self):
        return {
            "Branch": self.branch.name,
            "Product Model": self.product.model,
            "Quantity": self.quantity,
        }
    
class Serial(models.Model):
    serial = models.CharField(max_length=30, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.product.model} - {self.serial}"
    
    def to_excel_row(self):
        return {
            "Serial": self.serial,
            "Model": self.product.model,
            "Brand": self.product.brand,
        }

# class SerialImportTransaction(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     imported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     product = models.ForeignKey(Product, on_delete=models.PROTECT)
#     quantity = models.IntegerField()

#     def to_excel_row(self):
#         return {
#             "Created At": self.created_at.strftime("%Y-%m-%d %H:%M"),
#             "Imported By": self.imported_by.username if self.imported_by else "Unknown",
#             "Model": self.product.model,
#             "Quantity": self.quantity,
#         }