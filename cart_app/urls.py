from django.urls import path
from . import views


urlpatterns=[
   path('cart/',views.cart,name='cart'),
   path('add_to_cart/<int:product_id>/<str:size>/',views.add_to_cart,name='add_to_cart'),
   path('delete_from_cart/<int:item_id>/',views.delete_from_cart,name='delete_from_cart'),
   path('update-cart/<int:item_id>/',views.update_cart,name='update_cart'),
   path('checkout/',views.checkout,name='checkout'),
   path('add_checkout_address/',views.add_checkout_address,name='add_checkout_address'),

]
