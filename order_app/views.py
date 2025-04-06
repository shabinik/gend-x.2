from django.shortcuts import render,redirect,get_object_or_404
from . models import Order,OrderItem
from cart_app.models import Cart,CartItems
from account_app.models import Address,Wallet
from proapp.models import Products,Size_Varient
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from django.core.paginator import Paginator
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from coupon.models import Coupon
from transaction.models import Transaction

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.

def place_order(request):
    user = request.user
    if request.method == 'POST':
        address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment')

        if not address_id:
            messages.error(request,'You must select a address')
            return redirect('checkout')

        cart = get_object_or_404(Cart,user=user)
        cart_items = cart.cartitems.all()
    
        if not cart_items:
            messages.error(request,'Your cart is empty')
            return redirect('checkout')
        
        total_price = sum(item.total_price() for item in cart_items)
        real_price = total_price
        address=get_object_or_404(Address,id=address_id,user=user)

        discount_amount = 0  
        applied_coupon = None

        coupon_code = request.session.get('coupon_code')
        
        if coupon_code:
            try:
                applied_coupon = Coupon.objects.get(code=coupon_code)
                discount_amount = request.session.get('discount_amount')
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid or expired coupon.")
                applied_coupon = None


        final_price = max(total_price - discount_amount,0)
    
        if payment_method == 'razorpay':

            try:
                razorpay_order = razorpay_client.order.create({
                    'amount': int(final_price * 100),
                    'currency': "INR",
                    'payment_capture': 1
                })

                if not razorpay_order.get('id'):
                    messages.error(request,'Failed to generate Razorpay Order Id')
                    return redirect('checkout')
                
                order = Order.objects.create(
                    user=user,address=address,
                    payment_method=payment_method,
                    total_price=final_price,real_price=real_price,
                    discount_amount=discount_amount,
                    coupon=applied_coupon if applied_coupon else None,
                    status='failed',
                    razorpay_order_id = razorpay_order['id'],
                    created_at=timezone.now()
                )

                return redirect('razorpay_payment',order_id=order.id)
            except Exception as e:
                messages.error(request,f'Error: {str(e)}')
                return redirect('checkout')
        
        elif payment_method == 'COD':

            if final_price > 1000:
                messages.error(request,'Cash On Delivery is not applicable for Order greater than 1000')
                return redirect('checkout')
            
            with transaction.atomic():
                order = Order.objects.create(user=user,address=address,
                                             payment_method=payment_method,total_price=final_price,
                                             real_price=real_price,discount_amount=discount_amount,
                                             coupon=applied_coupon if applied_coupon else None)

                for item in cart_items:
                    size_varient = get_object_or_404(Size_Varient,product=item.product,size=item.size)

                    if size_varient.stock < item.quantity:
                        messages.error(request,'Insufficient stock')
                        transaction.set_rollback(True)
                        return redirect('checkout')
                    
                    if not item.product.is_active or not item.product.category.is_active:
                        messages.error(request,'Your Product or Category is Unlisted')
                        transaction.set_rollback(True)
                        return redirect('checkout')

                    size_varient.stock -= item.quantity
                    size_varient.save()
                    
                    item_total_price = item.product.price * item.quantity
                    item_discount = (item_total_price / total_price) * discount_amount if total_price > 0 else 0
                    price_per_item = max(0, (item_total_price - item_discount) / item.quantity) if item.quantity > 0 else 0
                    


                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=price_per_item,
                        size_varient=size_varient,
                        discount_amount=item_discount
                    )

                cart.cartitems.all().delete()
                request.session.pop('coupon_code', None)
                request.session.pop('discount_amount', None)
                cart.save()

            messages.success(request, "Your order has been placed successfully!")
            return redirect('order_success',order_id=order.id)
        


        elif payment_method == 'wallet':
            with transaction.atomic():
                wallet, created = Wallet.objects.get_or_create(user=request.user)

                if wallet.balance < final_price:
                    messages.error(request,'Insufficient Wallet balance')
                    return redirect('checkout')
                
                wallet.balance -= Decimal(final_price)
                wallet.save()
                order = Order.objects.create(user=user,address=address,
                                             payment_method=payment_method,total_price=final_price,
                                             real_price=real_price,discount_amount=discount_amount,
                                             coupon=applied_coupon if applied_coupon else None,status='paid')
                
                Transaction.objects.create(user=user,order=order,payment_method='Wallet',amount=final_price,status='paid')
                
                for item in cart_items:
                    size_varient = get_object_or_404(Size_Varient,product=item.product,size=item.size)

                    if size_varient.stock < item.quantity:
                        messages.error(request,'Insufficient stock')
                        transaction.set_rollback(True)
                        return redirect('checkout')
                
                    if not item.product.is_active or not item.product.category.is_active:
                        messages.error(request,'Your Product or Category is Unlisted')
                        transaction.set_rollback(True)
                        return redirect('checkout')
                    
                    size_varient.stock -= item.quantity
                    size_varient.save()

                    item_total_price = item.product.price * item.quantity
                    item_discount = (item_total_price / total_price) * discount_amount if total_price > 0 else 0
                    price_per_item = max(0, (item_total_price - item_discount) / item.quantity) if item.quantity > 0 else 0

                    
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        status = 'paid',
                        price=price_per_item,
                        size_varient=size_varient,
                        discount_amount=item_discount
                    )
                    
                cart.cartitems.all().delete()
                request.session.pop('coupon_code', None)
                request.session.pop('discount_amount', None)
                cart.save()

                messages.success(request,'Payment Successful!')
                return redirect('order_success',order_id=order.id)
                
    messages.error(request, "Invalid request")
    return redirect('checkout')

@csrf_exempt
def razorpay_payment(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id':order.razorpay_order_id
    }
    return render(request,'razorpay_payment.html',context)



@csrf_exempt
def razorpay_verify(request,order_id):
    if request.method == 'POST':
        try:
            data = request.POST
            razorpay_order_id = data.get('razorpay_order_id')
            payment_id = data.get('razorpay_payment_id')
            signature = data.get('razorpay_signature')

            order = get_object_or_404(Order,id=order_id,razorpay_order_id=razorpay_order_id)
            cart = get_object_or_404(Cart,user=request.user)
            cart_items = cart.cartitems.all()

            total_price = order.real_price
            discount_amount = order.discount_amount

            #payment signature verify
            params_dict = {
                'razorpay_order_id':razorpay_order_id,
                'razorpay_payment_id':payment_id,
                'razorpay_signature':signature
            }
            
            result = razorpay_client.utility.verify_payment_signature(params_dict)

            if result:
                with transaction.atomic():                   
                    order.status = 'paid'
                    order.razorpay_payment_id = payment_id
                    order.razorpay_signature = signature
                    order.save()
                
                    for item in cart_items:
                        size_varient = get_object_or_404(Size_Varient,product=item.product,size=item.size)

                        if size_varient.stock < item.quantity:
                            messages.error(request,'Insufficient stock')
                            transaction.set_rollback(True)
                            return redirect('checkout')
                        
                        if not item.product.is_active or not item.product.category.is_active:
                            messages.error(request,'Your Product is Unlisted')
                            transaction.set_rollback(True)
                            return redirect('checkout')
                    
                        size_varient.stock -= item.quantity
                        size_varient.save()

                        item_total_price = item.product.price * item.quantity
                        item_discount = (item_total_price / total_price) * discount_amount if total_price > 0 else 0
                        price_per_item = max(0, (item_total_price - item_discount) / item.quantity) if item.quantity > 0 else 0
                    
                        

                        OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        status = 'paid',
                        price=price_per_item,
                        size_varient=size_varient,
                        discount_amount=item_discount
                    )
                    
                    cart.cartitems.all().delete()
                    request.session.pop('coupon_code', None)
                    request.session.pop('discount_amount', None)
                    cart.save()

                    messages.success(request,'Payment Successful!')
                    return redirect('order_success',order_id=order.id)
                
            else:
                messages.error(request,'order failed')
                return redirect('order_failed',order_id=order_id)
    
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('order_failed', order_id=order.id)
        
    return JsonResponse({'error':'Invalid request'},status=400)

        
def retry_payment(request,order_id):
    order = get_object_or_404(Order,id=order_id,user=request.user)

    if order.status == 'paid':
        messages.error(request,'This order is already paid')
        return redirect('order_success',order_id=order_id)
    
    try:
        razorpay_order = razorpay_client.order.create({
            'amount': int(order.total_price * 100),
            'currency': "INR",
            'payment_capture': 1
        })

        if not razorpay_order.get('id'):
            messages.error(request, "Failed to generate a new payment order. Please try again.")
            return redirect('checkout')

        order.razorpay_order_id = razorpay_order['id']
        order.save()
        
        return redirect('razorpay_payment', order_id=order.id)
    
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('checkout')
    

def order_success(request,order_id):
    order = get_object_or_404(Order,id=order_id)
    return render(request,'order_success.html',{'order':order})

 
def order_failed(request,order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_failed.html', {'order': order})




def order_details(request,order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    order = get_object_or_404(Order,id=order_id,user=request.user)
    order_items = order.orderitem.all()
    for item in order_items:
        item.total_price = item.price * item.quantity

    context = {
        'order':order,
        'order_items':order_items,
    }
    return render(request,'order_details.html',context)



#------------------CANCEL ORDERS AND ORDER ITEMS--------------------------

def cancel_order(request,order_id):
    order = get_object_or_404(Order,id=order_id,user=request.user)
    
    if order.status == 'cancelled':
        messages.error(request,"Order already Cancelled")
        return redirect('order_details',order_id=order_id)
    
    if order.status == 'pending':
        with transaction.atomic():
            order.status = 'cancelled'
            order.save()

            for item in order.orderitem.all():
                size_varient = item.size_varient
                size_varient.stock += item.quantity
                size_varient.save()

                item.status = 'cancelled'
                item.save()
                messages.success(request,"Successfully Cancelled your Orders")
                return redirect('order_details',order_id=order_id)
    if order.status == 'paid':
        with transaction.atomic():
            order.status = 'cancelled'
            order.save()

            for item in order.orderitem.all():
                size_varient = item.size_varient
                size_varient.stock += item.quantity
                size_varient.save()

                item.status = 'cancelled'
                item.save()
            
            wallet, created = Wallet.objects.get_or_create(user=order.user)
            wallet.balance = Decimal(wallet.balance) + Decimal(order.total_price)
            wallet.save()

            Transaction.objects.create(user=request.user,order=order,payment_method='Wallet',
                                       amount=order.total_price,status='canceled')



        messages.success(request,"Successfully Cancelled your Orders")
        return redirect('order_details',order_id=order_id)


def cancel_order_item(request,order_id,order_item_id):
    order = get_object_or_404(Order,id=order_id,user=request.user)
    order_item = get_object_or_404(OrderItem,id=order_item_id,order=order)
    
    remaining_items = order.orderitem.exclude(id=order_item.id).filter(status__in=['pending','paid']).count()

    if remaining_items == 0:
        messages.error(request, "You cannot cancel the last item in the order.")       
        return redirect('order_details', order_id=order_id)
    
    if order_item.status == 'cancelled':
        messages.error(request,"This Item is already Cancelled")
        return redirect('order_details',order_id=order_id)
    
    if order_item.status == 'pending':
        with transaction.atomic():
            order_item.status = 'cancelled'
            order_item.save()

            size_varient = order_item.size_varient
            size_varient.stock += order_item.quantity
            size_varient.save()
            messages.success(request,'Successfully Cancelled Item ')
            return redirect('order_details',order_id=order_id)
    else:
        with transaction.atomic():
            order_item.status = 'cancelled'
            order_item.save()

            size_varient = order_item.size_varient
            size_varient.stock += order_item.quantity
            size_varient.save()
            

            order_item.total_price = order_item.price * order_item.quantity

            wallet,created = Wallet.objects.get_or_create(user=order.user)
            wallet.balance = Decimal(wallet.balance) + Decimal(order_item.total_price)
            wallet.save()
            order.total_price -= order_item.total_price
            order.save()

            Transaction.objects.create(user=request.user,order=order,payment_method='Wallet',
                                       amount=order_item.total_price,status='canceled')

        messages.success(request,'Successfully Cancelled Item ')
        return redirect('order_details',order_id=order_id)


#---------------------RETURN ORDER AND ORDER ITEMS----------------------------------


def request_return_order(request,order_id):
    order = get_object_or_404(Order,id=order_id,user=request.user)

    if order.status != 'delivered':
        messages.error(request,"Only delivered orders can be requested for return.")
        return redirect('order_details',order_id=order_id)
    
    if order.status in ['pending_return', 'returned', 'cancelled']:
        messages.warning(request, "This order cannot be requested for return .")
        return redirect('order_details', order_id=order_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')

        if not reason:
            messages.error(request, "Please provide a reason for the return request.")
            return redirect('order_details', order_id=order_id)
        
        order.request = 'requested'
        order.status = 'pending_return'
        order.reason = reason
        order.save()

        for item in order.orderitem.all():
                item.status = 'pending_return'
                item.save()

    messages.success(request, "Your return request has been submitted. The admin will review it.")
    return redirect('order_details', order_id=order_id)
    
    

def admin_approve_return(request,order_id):
    order = get_object_or_404(Order,id=order_id)

    if order.status != 'pending_return' or order.request != 'requested':
        messages.error(request, "This order is not pending return approval.")
        return redirect('admin_order_details', order_id=order_id)
    
    action = request.POST.get('action')

    if order.request == 'requested':        
        if action == 'approved':
            order.request = 'approved'
            order.status='returned'
            order.save()

            for item in order.orderitem.all():
                item.status = 'returned'
                item.save()
                size_varient = item.size_varient
                size_varient.stock += item.quantity
                size_varient.save()

            wallet, created = Wallet.objects.get_or_create(user=order.user)
            wallet.balance = Decimal(wallet.balance) + Decimal(order.total_price)
            wallet.save()

            Transaction.objects.create(user=order.user,order=order,payment_method='Wallet',
                                       amount=order.total_price,status='returned')

            messages.success(request,'Return request has been approved and processed successfully')
            return redirect('admin_order_details',order_id=order_id)
    
        elif action == 'rejected':
            order.request = ''
            order.status = 'delivered'
            order.save()
            for item in order.orderitem.all():
                item.status = 'delivered'
                item.save()
            messages.error(request,'Return is rejected')
            return redirect('admin_order_details',order_id=order_id)

        else:
            messages.error(request, 'Invalid action!')


        return redirect('admin_order_details',order_id=order_id)
            



def return_order_item(request,order_id,order_item_id):
    order = get_object_or_404(Order,id=order_id,user=request.user)
    order_item = get_object_or_404(OrderItem,id=order_item_id,order=order)

    remaining_items = order.orderitem.exclude(id=order_item.id).filter(status='delevered').count()

    if remaining_items == 0:
        messages.error(request, "You cannot cancel the last item in the order.")
        return redirect('order_details', order_id=order_id)

    if order_item.status in ['cancelled','failed','returned']:
        messages.error(request,'This Item has already been processed for return or cancellation.')
        return redirect('order_details',order_id=order_id)
    
    with transaction.atomic():
        order_item.status = 'returned'
        order_item.save()

        size_varient = order_item.size_varient
        size_varient.stock += order_item.quantity
        size_varient.save()

        order_item.total_price = order_item.price * order_item.quantity

        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet.balance = Decimal(wallet.balance) + Decimal(order_item.total_price)
        wallet.save()

        order.total_price -= order_item.total_price
        order.save()

        Transaction.objects.create(user=request.user,order=order,payment_method='Wallet',
                                       amount=order_item.total_price,status='returned')

    messages.success(request,'Successfully returned Your Item')
    return redirect('order_details',order_id=order_id)





#---------------- ADMIN SIDE----------------------

def order_list(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    order = Order.objects.order_by('-id').all()
    search = request.GET.get('search','')

    if search:
        orders = Order.objects.filter(
            Q(user__username__icontains=search)|Q(user__email__icontains=search)
        )
    else:
        orders = order
    return render(request,'admin_pages/order_list.html',{'orders':orders})


#ORDER DETAILS IN ADMIN

def admin_order_details(request,order_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    order = get_object_or_404(Order,id=order_id)
    order_items = order.orderitem.all()
    for item in order_items:
        item.total_price = item.price * item.quantity 

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(order.ORDER_STATUS_CHOICES):
            if new_status == 'pending' and order.status in ['completed','delivered']:
                messages.error(request,'This order cant change to pending')
                return redirect('admin_order_details',order_id=order_id)
            order.status = new_status
            order.save()
            for item in order.orderitem.all():
                item.status = new_status
                item.save()
        
    return render(request,'admin_pages/admin_order_details.html',{'order':order,'order_items':order_items})







    

#----------------------------------DOWNLOAD INVOICE--------------------------------------


def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Invoice")

    # Order Details
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Order ID: {order.id}")
    p.drawString(50, height - 120, f"Customer: {order.user.username}")
    p.drawString(50, height - 140, f"Date: {order.created_at.strftime('%Y-%m-%d')}")

    # Table Header
    y_position = height - 180
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, "Product")
    p.drawString(250, y_position, "Quantity")
    p.drawString(350, y_position, "Price")

    # Table Data
    p.setFont("Helvetica", 12)
    y_position -= 20
    for item in order.orderitem.all():
        p.drawString(50, y_position, item.product.name)
        p.drawString(250, y_position, str(item.quantity))
        p.drawString(350, y_position, f"${item.price:.2f}")
        y_position -= 20

    # Total Price
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position - 20, f"Total Price: ${order.total_price:.2f}")

    p.showPage()
    p.save()
    
    return response


