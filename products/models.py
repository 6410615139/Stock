from django.db import models

class Product(models.Model):
    image = models.ImageField(upload_to='product_images/')
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    warranty_period = models.PositiveIntegerField()  # in months

    def is_claim_active(self):
        from datetime import date, timedelta
        expiry_date = self.purchase_date + timedelta(days=self.warranty_period * 30)
        return date.today() <= expiry_date

    def __str__(self):
        return f"{self.name} ({self.serial_number})"
