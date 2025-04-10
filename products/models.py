from django.db import models

class Product(models.Model):
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    EAN_code = models.CharField(max_length=20)
    dealer_price = models.FloatField()
    volumn_price = models.FloatField()
    MSRP = models.FloatField()

    def __str__(self):
        return f"{self.brand} | {self.model}"


class Serial(models.Model):
    serial = models.CharField(max_length=30, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='serials')

    def __str__(self):
        return f"{self.serial} - {self.product.model}"


class Transaction(models.Model):
    model = models.CharField(max_length=30)
    quantity = models.IntegerField()
    source = models.CharField(max_length=30)
    destination = models.CharField(max_length=30)

    def __str__(self):
        return f"Transaction of {self.quantity} {self.model} from {self.source} to {self.destination}"


class Branch(models.Model):
    branch = models.CharField(max_length=30)
    # details = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.branch


class BranchProduct(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.branch.branch} - {self.product.model} ({self.quantity})"
