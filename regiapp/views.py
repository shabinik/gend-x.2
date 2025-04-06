from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from . forms import RegistrationForm,LoginForm
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
import random,time
from django.utils.timezone import now
from django.contrib.auth import update_session_auth_hash
from . models import Referral
from account_app.models import Wallet
from decimal import Decimal
from transaction.models import Transaction


# Create your views here.

#function for send OTP

def send_otp(email):
    otp= random.randint(100000, 999999)
    subject= "Your OTP code"
    message= f"Your OTP for registration is {otp}."
    send_mail(subject, message, settings.EMAIL_HOST_USER,[email])

    return otp


# -------------Registration View -------------------------------

def register_view(request):
    if request.method=="POST":
        form=RegistrationForm(request.POST)
        if form.is_valid():
            referral_code = form.cleaned_data.get('referral_code')
            referred_by = None
            if referral_code:
                referrer = Referral.objects.filter(referral_code=referral_code).first()
                if referrer:
                    referred_by = referrer.user

            request.session['register_data']={
                "username":form.cleaned_data['username'],
                "email":form.cleaned_data["email"],
                "password":form.cleaned_data["password"],
                "referral_code":referral_code, 
            }

            otp=send_otp(form.cleaned_data["email"])
            request.session["otp"]=str(otp)
            request.session['otp_time']=time.time()
            return redirect('verify_otp')
        else:
            messages.error(request,'Please correct the errors below!')
    else:
        form=RegistrationForm()

    return render(request,'register.html',{"form":form})




#VERIFY OTP-------

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        otp_time = request.session.get('otp_time')
        user_data = request.session.get('register_data')

        if not stored_otp or not user_data:
            messages.error(request,"Session time out register again")
            return redirect('register')


        if not otp_time or time.time() - otp_time > 120:
            messages.error(request,"OTP expired, Request for a new one")
            return redirect('resend_otp')
        
        if entered_otp==str(stored_otp):
            user=User.objects.create_user(
                username=user_data["username"],
                email=user_data["email"],
            )
            user.set_password(user_data["password"])
            user.save()
            
            referred_by = None
            referral_code = user_data.get('referral_code', '').strip() 
            if referral_code:
                referrer = Referral.objects.filter(referral_code=referral_code).first()
                if referrer:
                    referred_by = referrer.user 

            if not Referral.objects.filter(user=user).exists():
                if referred_by:
                    Referral.objects.create(user=user,referred_by=referred_by)
                else:
                    Referral.objects.create(user=user)

    
            Wallet.objects.create(user=user,balance=100)
            Transaction.objects.create(user=user,amount=100,status='referral')
            
            if referred_by:
                referrer_wallet = Wallet.objects.filter(user=referred_by).first()
                if referrer_wallet:
                    referrer_wallet.balance += Decimal(100)
                    referrer_wallet.save()
                    Transaction.objects.create(user=referred_by,amount=100,status='referral')
            
            
            messages.success(request,"OTP verified Successfully! Created account")

            del request.session["otp"]
            del request.session['otp_time']
            del request.session['register_data']

            return redirect('login')
        else:
            messages.error(request,"Invalid OTP! Try again")
    
    return render(request,'verify_otp.html')


#Resend OTP------

def resend_otp(request):
    user_data=request.session.get('register_data')
    if not user_data:
        messages.error(request,"Session time out register again")
        return redirect('register')
    del request.session["otp"]
    del request.session["otp_time"]    
    otp=send_otp(user_data['email'])
    request.session['otp']=str(otp)
    request.session['otp_time']=time.time()

    request.session.modified=True

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_otp')

#--------------Login View-----------------------------------

def login_view(request):
    if request.method=="POST":
        form=LoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data["username"]
            password=form.cleaned_data["password"]
            user=authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                messages.success(request,"Login successfull!")
                return redirect(reverse("mainapp:home"))
            else:
                messages.error(request,"Invalid username or password")
    else:
        form=LoginForm()
        
    return render(request,'login.html',{"form": form})

#------------------------------FORGOT PASSWORD--------------------------------------

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request,'Email does not exist. Please  register as a new User')
            return redirect('forgot_password')
        else:
            otp=send_otp(email)
            request.session['forgot_otp']=str(otp)
            request.session['user_id'] =user.id
            request.session['forgot_otp_time']=time.time()
            return redirect('forgot_otp_verify')
        
    return render(request,'forgot_password.html')



def forgot_otp_verify(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('forgot_otp')
        forgot_otp_time = request.session.get('forgot_otp_time')
        user_id = request.session.get('user_id')

        if not stored_otp or not user_id:
            messages.error(request,"Session time out come again")
            return redirect('forgot_password')
        
        if not forgot_otp_time or time.time() - forgot_otp_time > 120:
            messages.error(request,"OTP expired, Request for a new one")
            return redirect('forgot_resend_otp')
        
        if entered_otp==str(stored_otp):
            messages.success(request,"OTP verified Successfully! Set new Password!")

            del request.session["forgot_otp"]
            del request.session['forgot_otp_time']

            return redirect('set_new_password',user_id=user_id)
        else:
            messages.error(request,"Invalid OTP! Try again")
    
    
    return render(request,'forgot_otp_verify.html')

def forgot_resend_otp(request):
    user_id=request.session.get('user_id')
    user = User.objects.get(id=user_id)
    if not user_id:
        messages.error(request,"Session time out come again")
        return redirect('forgot_password')
    del request.session["forgot_otp"]
    del request.session["forgot_otp_time"]    
    otp=send_otp(user.email)
    request.session['forgot_otp']=str(otp)
    request.session['forgot_otp_time']=time.time()

    request.session.modified=True

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('forgot_otp_verify')

def set_new_password(request,user_id):
    user = get_object_or_404(User,id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request,'Confirm password is not match')
            return redirect('set_new_password',user_id=user_id )
        
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request,user)
        messages.success(request,'Password changed successfully')
        return redirect('login')
    return render(request,'set_new_password.html') 
