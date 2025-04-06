"""
URL configuration for ecom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('mainapp.urls')),
    path('user_registration/',include('regiapp.urls')),
    path('category/',include('catapp.urls')),
    path('product/',include('proapp.urls')),
    path('',include('admin_auth.urls')),
    path('accounts/',include('allauth.urls')),
    path('user_account/',include('account_app.urls')),
    path('user_cart/',include('cart_app.urls')),
    path('order/',include('order_app.urls')),
    path('wishlist/',include('wishlist.urls')),
    path('coupon/',include('coupon.urls')),
    path('transaction/',include('transaction.urls')),
]
