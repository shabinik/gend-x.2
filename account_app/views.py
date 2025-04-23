from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,logout
from django.contrib.auth.models import User
from . models import Address,Wallet
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from order_app.models import Order
from regiapp.models import Referral
from transaction.models import Transaction

# Create your views here.

#MY ACCOUNT

def my_account(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user=request.user
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(user=user)

    referral = Referral.objects.filter(user=user).first()
    referral_code = referral.referral_code if referral else None
    context = {
        'user':user,
        'addresses':addresses,
        'orders':orders,
        'wallet':wallet,
        'referral_code':referral_code,
        'transactions':transactions
    }
    return render(request,'my_account.html',context)


def edit_profile(request,id):
    user=get_object_or_404(User,id=id)

    if request.method == 'POST':
        username = request.POST.get('username')
        
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'This username is already in use. Please use a different one.')
        else:            
            user.username = username
            user.save()
            return redirect('my_account')
    return render(request,'edit_profile.html',{'user':user})


# ADD ADDRESS

def add_address(request):

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
                return redirect('add_address')
        except ValueError:
            messages.error(request, 'Error in validation')
            return redirect('add_address')

        address = Address.objects.create(user=user,full_name=full_name,city=city,state=state,postal_code=postal_code,landmark=landmark,phone_no=phone_no)
        return redirect('display_address')
    return render(request,'add_address.html')



#DISPLAY ADDRESS
@login_required
def display_address(request):
    user = request.user
    print("User:", user, "Authenticated:", user.is_authenticated)
    addresses = Address.objects.filter(user=user).all()
    return render(request,'my_account.html',{'addresses':addresses})

#EDIT ADDRESS

def edit_address(request,id):
    address = get_object_or_404(Address,id=id,user=request.user)
    if request.method == 'POST':
        user = request.user
        full_name = request.POST.get('full_name')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        landmark = request.POST.get('landmark')
        phone_no = request.POST.get('phone_no')

        address.user = user
        address.full_name = full_name
        address.city = city
        address.state = state
        address.postal_code = postal_code
        address.landmark = landmark
        address.phone_no = phone_no
        address.save()
        return redirect('display_address')
    return render(request,'edit_account.html',{'address':address})
    
# DELETE ADDRESS

def delete_address(request,id):
    address = get_object_or_404(Address,id=id,user=request.user)
    address.delete()
    return redirect('display_address')


#CHANGE PASSWORD

def change_password(request):
    
    if request.method == 'POST':
        user = request.user
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not check_password(current_password,user.password):
            messages.error(request,'Current password is not match')
            return redirect('my_account')
        if new_password != confirm_password:
            messages.error(request,'Confirm password is not match')
            return redirect('my_account')
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request,user)
        messages.success(request,'Password changed successfully')
        return redirect('my_account')
    return redirect('my_account')    
    





#USER LOGOUT

def user_logout(request):
    logout(request)
    return redirect('login')
