from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns=[
    path('',views.register_view,name='register'),
    path('login/',views.login_view,name='login'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('resend_otp/',views.resend_otp,name='resend_otp'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('forgot_otp_verify/',views.forgot_otp_verify,name='forgot_otp_verify'),
    path('set_new_password/<int:user_id>/',views.set_new_password,name='set_new_password'),
    path('forgot_resend_otp/',views.forgot_resend_otp,name='forgot_resend_otp'),
]    


