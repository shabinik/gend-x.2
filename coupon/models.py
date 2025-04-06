from django.db import models
from django.utils import timezone


# Create your models here.

class Coupon(models.Model):
    code = models.CharField(max_length=50,unique=True)
    discount = models.IntegerField()
    min_purchase_amount = models.DecimalField(max_digits=30, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Check if the coupon is active and within the validity period"""
        today = timezone.now().date()
        return self.valid_from <= today <= self.valid_to
    
    def __str__(self):
        return self.code
