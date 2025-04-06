from django.shortcuts import render,redirect,get_object_or_404
from . models import Cart,CartItems
from proapp.models import Products,Size_Varient
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from account_app.models import Address
from django.contrib import messages
from coupon.models import Coupon



# Create your views here.

#CART DETAILS

def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    cart,created = Cart.objects.get_or_create(user=user)
    cart_items = cart.cartitems.all()
    total_price = sum(item.total_price() for item in cart_items)

    return render(request,'cart.html',{'cart_items':cart_items,'total_price':total_price})
    



#ADD TO CART
@login_required
def add_to_cart(request,product_id,size):
    product = get_object_or_404(Products,id = product_id)
    size_varient = product.size_varient.filter(size=size).first()
    stock = size_varient.stock if size_varient else 0
    if stock == 0:
        return redirect('mainapp:product_detail',product_id)
    cart,created = Cart.objects.get_or_create(user = request.user)

    if not product.is_active or not product.category.is_active:
        return redirect('cart') 
    cart_item,created = CartItems.objects.get_or_create(cart=cart, product=product, size=size)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item.quantity = 1
        cart_item.save()

    cart.total_price = sum(item.total_price() for item in cart.cartitems.all())
    cart.save()
    
    return redirect('cart')

#UPDATE CART

def update_cart(request,item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItems,id=item_id,cart__user= request.user)
        new_quantity = int(request.POST.get('quantity'))

        if new_quantity < 1:
            new_quantity = 1

        cart_item.quantity = new_quantity
        cart_item.save()
        
        cart = cart_item.cart
        total_price = sum(item.total_price() for item in cart.cartitems.all())
        return JsonResponse({
            "success": True,
            "subtotal": cart_item.total_price(),
            "total_price": total_price,
        })
    return JsonResponse({"success": False, "error": "Invalid request"})



def delete_from_cart(request,item_id):
    cart_item = get_object_or_404(CartItems,id=item_id,cart__user=request.user)
    cart_item.delete()

    return redirect('cart')


# ---------CHECKOUT-------

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        user = request.user

        cart = Cart.objects.get(user = user)
        cart_items = cart.cartitems.all()

        if not cart_items.exists():
            messages.error(request,'Your cart is empty, Add Items to Continue with checkout')
            return redirect('cart')
        
        total_price = sum(item.total_price() for item in cart_items)
        address = Address.objects.filter(user=user)
        coupons = Coupon.objects.order_by('-id').all()
        coupon_code = request.session.get('coupon_code',None)
        discount_amount = request.session.get('discount_amount',0)
        final_price = max(total_price - discount_amount,0)

        context = {
            'items':cart_items,
            'original_price':total_price,
            'total_price':final_price,
            'address':address,
            'coupons':coupons,
            'coupon_code':coupon_code,
            'discount_amount':discount_amount
        }


        return render(request,'checkout.html',context)
    except Cart.DoesNotExist:
        messages.error(request,'Your Cart is doesnot exist')
        return redirect('cart')


def add_checkout_address(request):

    error = None

    if request.method == 'POST':
        user = request.user
        full_name=request.POST.get('full_name')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        landmark = request.POST.get('landmark')
        phone_no = request.POST.get('phone_no')

        try:
            phone_no = str(phone_no)
            if not phone_no.isdigit() or len(phone_no) != 10:
                messages.error(request, 'Phone number must be exactly 10 digits')
                return redirect('add_checkout_address')
        except ValueError:
            messages.error(request, 'Error in validation')
            return redirect('add_checkout_address')
        address = Address.objects.create(user=user,full_name=full_name,city=city,state=state,postal_code=postal_code,landmark=landmark,phone_no=phone_no)
        return redirect('checkout')
    return render(request,'add_address.html')

    

    

