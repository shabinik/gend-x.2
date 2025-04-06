from django import forms
from django.contrib.auth.models import User
import re

#Registration form
class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput)
    password2=forms.CharField(widget=forms.PasswordInput,label="Confirm password")


    class Meta:
        model=User
        fields=['username','email']

    def clean_username(self):
        username=self.cleaned_data.get('username', '').strip()

        if len(username) < 4:
            raise forms.ValidationError("Username should have min 4 letters")
        if " " in username:
            raise forms.ValidationError("Username cannot contains space")
        return username

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

    


#Login form

class LoginForm(forms.Form):
    username=forms.CharField(max_length=100)
    password=forms.CharField(widget=forms.PasswordInput)



    