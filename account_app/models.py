from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Address(models.Model):
    user=models.ForeignKey(User,related_name='address',on_delete=models.CASCADE)
    full_name=models.CharField(max_length=50)
    city=models.CharField(max_length=45)
    state=models.CharField(max_length=40)
    postal_code=models.CharField(max_length=10)
    landmark=models.CharField(max_length=50,blank=True,null=True)
    phone_no=models.CharField(max_length=15)
    default=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name
    

class Wallet(models.Model):
    user = models.OneToOneField(User,related_name='wallet',on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=25,decimal_places=2,default=0.00)
    
    def __str__(self):
        return f"{self.user.username}'s Wallet - Balance: {self.balance}"
