from django.urls import path
from . import views


urlpatterns=[
    path('wishlist/',views.wishlist,name='wishlist'),
    path('add_to/wishlist/<int:product_id>/<str:size>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('del/wishlist_item/<int:item_id>/',views.del_wish_item,name='del_wish_item'),
]
    