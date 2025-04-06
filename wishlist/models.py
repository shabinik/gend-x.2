from django.db import models
from proapp.models import Products
from django.contrib.auth.models import User

# Create your models here.

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'wishlist of {self.user.username}'
    

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist,related_name='wishlistitems',on_delete=models.CASCADE)
    product = models.ForeignKey(Products,related_name='wishlistitems',on_delete=models.CASCADE)
    size = models.CharField(max_length=20,default='M')
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f'{self.quantity}x {self.product.name} (Size: {self.size}) in {self.wishlist.user.username}\'s Wishlist'

        