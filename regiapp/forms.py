from django import forms
from django.contrib.auth.models import User
from . models import Referral
import re

#Registration form
class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput)
    password2=forms.CharField(widget=forms.PasswordInput,label="Confirm password")
    referral_code = forms.CharField(required=False,max_length=50)


    class Meta:
        model=User
        fields=['username','email']

    def clean_username(self):
        username=self.cleaned_data.get('username', '').strip()

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This Username is already exist Use different username')

        if len(username) < 4:
            raise forms.ValidationError("Username should have min 4 letters")
        if " " in username:
            raise forms.ValidationError("Username cannot contains space")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email','').strip()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This Email already used please use another one')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pattern,password):
            raise forms.ValidationError(
                "Password contains atleast 8 charecters,"
                "contains atleast 1 uppercase and lowercase letter,"
                "1 number, and 1 special charecter (@$!%*?&)."
            )
        return password

    def clean_password2(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            raise forms.ValidationError("Password donot match!")
        return self.cleaned_data.get('password2')
    
    def clean_referral_code(self):
        referral_code = self.cleaned_data.get('referral_code','').strip()
        if referral_code and not Referral.objects.filter(referral_code=referral_code).exists():
            forms.ValidationError('Invalid referral code')
        return referral_code
    


#Login form

class LoginForm(forms.Form):
    username=forms.CharField(max_length=100)
    password=forms.CharField(widget=forms.PasswordInput)



    