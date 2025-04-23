from django.shortcuts import render,redirect,get_object_or_404
from . models import Coupon
from . forms import CouponApplyForm,CouponForm
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from cart_app.models import Cart

# Create your views here.



def apply_coupon(request):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']
            
            try:
                coupon = Coupon.objects.get(code=code, is_active=True)  # FIXED typo

                if not coupon.is_valid():
                    messages.error(request, 'Coupon is expired or not active')
                    return redirect('checkout')

                cart = get_object_or_404(Cart, user=request.user)
                cart_items = cart.cartitems.all()
                total_price = sum(item.total_price() for item in cart_items)

                if total_price < coupon.min_purchase_amount:
                    messages.error(request, f'Minimum purchase should be {coupon.min_purchase_amount}')
                    return redirect('checkout')


                coupon_discount = coupon.discount / 100  
                discount_amount = total_price * coupon_discount
        
                discount_amount = max(discount_amount, 0)

                request.session['coupon_code'] = coupon.code
                request.session['discount_amount'] = float(discount_amount)

                messages.success(request, f'Coupon {coupon.code} applied successfully!')
                return redirect('checkout')

            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid Coupon code')
                return redirect('checkout')

    return redirect('checkout')




def remove_coupon(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        del request.session['discount_amount']
        messages.success(request,'Coupon removed Successfully')
        return redirect('checkout')



def create_coupon(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()    
            return redirect('coupon_list')
        else:
            messages.error(request, "Error creating coupon. Please check the form.")
    else:
        form = CouponForm()
    return render(request,'admin_pages/coupon.html',{'form':form})


def coupon_list(request):
     if not request.user.is_superuser:
        return redirect('admin_login')
     
     coupons = Coupon.objects.order_by('-id').all()
     form = CouponForm()
     return render(request,'admin_pages/coupon.html',{'coupons':coupons,'form':form})




def edit_coupon(request,id):
    coupon = get_object_or_404(Coupon,id=id)

    if request.method == 'POST':
        code = request.POST.get('code','').strip()
        discount = int(request.POST.get('discount',0))
        min_purchase_amount = float(request.POST.get('min_purchase_amount',0))
        valid_from = parse_datetime(request.POST.get('valid_from'))
        valid_to = parse_datetime(request.POST.get('valid_to'))
        usage_limit = int(request.POST.get('usage_limit',1))

        coupon.code = code
        coupon.discount = discount
        coupon.min_purchase_amount = min_purchase_amount
        coupon.valid_from = valid_from
        coupon.valid_to = valid_to
        coupon.usage_limit = usage_limit
        coupon.save()
        return redirect('coupon_list')
    
    return render(request,'admin_pages/edit_coupon.html',{'coupon':coupon})


def delete_coupon(request,id):
    coupon = get_object_or_404(Coupon,id=id)
    coupon.delete()

    return redirect('coupon_list')