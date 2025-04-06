from django.db import models
from catapp.models import Categories
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User

# Create your models here.

class Products(models.Model):
    category=models.ForeignKey(Categories,related_name='products',on_delete=models.CASCADE)
    name=models.CharField(max_length=50)
    description=models.TextField()
    price=models.IntegerField()
    offer=models.DecimalField(max_digits=5,decimal_places=2)
    image1=CloudinaryField('image')
    image2=CloudinaryField('image')
    image3=CloudinaryField('image')
    is_active=models.BooleanField(default=True)
    rating=models.IntegerField(default=0,null=True,blank=True)

    def __str__(self):
        return self.name


class Size_Varient(models.Model):
    product=models.ForeignKey(Products,related_name='size_varient',on_delete=models.CASCADE)
    size=models.CharField(max_length=15)
    stock=models.IntegerField(default=0)

    def __str__(self):
        return super().__str__()
     