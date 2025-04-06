from django.db import models
from django.contrib.auth.models import User
from proapp.models import Products,Size_Varient
from account_app.models import Address
from coupon.models import Coupon

# Create your models here.

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending','pending'),
        ('completed','completed'),
        ('cancelled','cancelled'),
        ('delivered','delivered'),
        ('paid','paid'),
        ('failed','failed'),
    ]
    user = models.ForeignKey(User,related_name='order',on_delete=models.CASCADE)
    address = models.ForeignKey(Address,related_name='order',on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=50,decimal_places=2)
    real_price = models.DecimalField(max_digits=50,decimal_places=2)
    status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES,default='pending')
    discount_amount = models.DecimalField(max_digits=20,decimal_places=2,default=0.00,null=True,blank=True)
    coupon = models.ForeignKey(Coupon,related_name='order',on_delete=models.CASCADE,null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=225,null=True)
    razorpay_payment_id = models.CharField(max_length=225,null=True,blank=True)
    razorpay_signature = models.CharField(max_length=225, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reason = models.TextField(null=True,blank=True)
    request = models.TextField(null=True,blank=True)

    def __str__(self):
        return f'Order #{self.id} - {self.user.username}'
    


class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='orderitem',on_delete=models.CASCADE)
    product = models.ForeignKey(Products,related_name='orderitem',on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=50,decimal_places=2)
    size_varient = models.ForeignKey(Size_Varient,related_name='orderitem',on_delete=models.CASCADE)
    status = models.CharField(max_length=50,default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reason = models.TextField(null=True,blank=True)
    discount_amount = models.DecimalField(max_digits=20,decimal_places=2,default=0.00,null=True,blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
