from django.urls import path
from . import views

app_name="mainapp"

urlpatterns=[
    path('',views.index,name='home'),
    path('shop/',views.shop,name='shop'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('cart/',views.cart,name='cart'),
    path('product_detail/<int:id>',views.product_detail,name='product_detail'),
]