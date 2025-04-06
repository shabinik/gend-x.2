from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns=[
    path('',views.register_view,name='register'),
    path('login/',views.login_view,name='login'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('resend_otp/',views.resend_otp,name='resend_otp'),

]


