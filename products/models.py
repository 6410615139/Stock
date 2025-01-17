from django.db import models
from datetime import date, timedelta

class Product(models.Model):
    image = models.ImageField(upload_to='product_images/')
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    warranty_period = models.PositiveIntegerField()  # in months
    tstamp = models.DateTimeField(auto_now_add=True)

    def is_claim_active(self):
        expiry_date = self.purchase_date + timedelta(days=self.warranty_period * 30)
        return date.today() <= expiry_date

    def warranty_days_left(self):
        expiry_date = self.purchase_date + timedelta(days=self.warranty_period * 30)
        remaining_time = expiry_date - date.today()
        return max(remaining_time.days, 0)  # Returns 0 if the warranty has expired

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class ProductHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="histories")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    claim_active = models.BooleanField()

    def __str__(self):
        return f"History for {self.product.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
