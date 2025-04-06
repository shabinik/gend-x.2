from django.db import models
from django.contrib.auth.models import User
import random
import string

# Create your models here.


class Referral(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=50,unique=True,blank=True)
    referred_by = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True,related_name='referrals')

    def generate_referral_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def save(self,*args,**kwargs):
        if not self.referral_code:
            self.referral_code= self.generate_referral_code()    
        super().save(*args,**kwargs)

