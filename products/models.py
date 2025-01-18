from django.db import models
from datetime import date, timedelta
from django.core.validators import MaxValueValidator, MinValueValidator

class Product(models.Model):
    image = models.ImageField(upload_to='product_images/')
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    warranty_period = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(999)],
        null=True, # Allow null for "forever"
        blank=True
    )
    tstamp = models.DateTimeField(auto_now_add=True)

    def is_warranty_forever(self):
        return self.warranty_period is None

    def get_warranty_display(self):
        if self.is_warranty_forever():
            return "Forever"
        return f"{self.warranty_period} months"

    def is_claim_active(self):
        if self.is_warranty_forever():
            return True
        expiry_date = self.purchase_date + timedelta(days=self.warranty_period * 30)
        if date.today() <= expiry_date:
            return True
        return False

    def warranty_days_left(self):
        if self.is_warranty_forever():
            return None
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
