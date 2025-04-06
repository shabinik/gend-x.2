from django.db import models
import cloudinary
from cloudinary.models import CloudinaryField

# Create your models here.

class Categories(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField()
    offer=models.DecimalField(max_digits=5,decimal_places=2)
    image=CloudinaryField('image',null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)


    def __str__(self):
        return self.name


