from django.db import models
from django.contrib.auth.models import User
from proapp.models import Products

# Create your models here.


# CART MODELS
class Cart(models.Model):
    user = models.ForeignKey(User,related_name='cart',on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart of {self.user.username}'
    
# CART ITEMS MODEL
class CartItems(models.Model):
    cart = models.ForeignKey(Cart,related_name='cartitems',on_delete=models.CASCADE)
    product = models.ForeignKey(Products,related_name='cartitems',on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10,default='M')

    def total_price(self):
        return self.product.price*self.quantity
    def __str__(self):
        return super().__str__
    def return_stock(self):
        return self.product.size_varient.stock



