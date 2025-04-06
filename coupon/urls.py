from django.urls import path
from . import views


urlpatterns=[
    path('create/coupon',views.create_coupon,name='create_coupon'),
    path('apply/coupon',views.apply_coupon,name='apply_coupon'),
    path('coupon/list',views.coupon_list,name='coupon_list'),
    path('edit/coupon/<int:id>/',views.edit_coupon,name='edit_coupon'),
    path('delete/coupon/<int:id>/',views.delete_coupon,name='delete_coupon'),
    path('remove_coupon/',views.remove_coupon,name='remove_coupon'),
]