from django import forms
from . models import Coupon




class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code','discount','min_purchase_amount','valid_from','valid_to','usage_limit']
        widgets = {
            'valid_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valid_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter coupon code'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount'}),
            'min_purchase_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter minimum purchase amount'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter usage limit'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code').strip() 
        if Coupon.objects.filter(code__iexact=code).exists(): 
            raise forms.ValidationError("This coupon code already exists. Please use a unique code.")
        return code


class CouponApplyForm(forms.Form):
    code = forms.CharField(label = 'Coupon code')

    def clean_code(self):
        code = self.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            if not coupon.is_valid():
                raise forms.ValidationError('This Coupen has Expired')
            
        except Coupon.DoesNotExist:
            raise forms.ValidationError('Invalid Coupon Code')
        
        return code
    


