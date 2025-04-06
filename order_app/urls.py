from django.urls import path
from . import views


urlpatterns=[
    path('place_order/',views.place_order,name='place_order'),
    path('order/success/<int:order_id>/',views.order_success,name='order_success'),
    path('order_details/<int:order_id>/',views.order_details,name='order_details'),
    path('cancel_order/<int:order_id>/',views.cancel_order,name='cancel_order'),
    path('cancel/order_item/<int:order_id>/<int:order_item_id>/',views.cancel_order_item,name='cancel_order_item'),
    path('request/return_order/<int:order_id>/',views.request_return_order,name='request_return_order'),
    path('return/order_item/<int:order_id>/<int:order_item_id>/',views.return_order_item,name='return_order_item'),
    path('admin/approve_return/<int:order_id>/',views.admin_approve_return,name='admin_approve_return'),
    path('order_list/',views.order_list,name='order_list'),
    path('admin/order_details/<int:order_id>/',views.admin_order_details,name='admin_order_details'),
    path("invoice/<int:order_id>/", views.generate_invoice, name="generate_invoice"),
    path('razorpay/payment/<int:order_id>',views.razorpay_payment,name='razorpay_payment'),
    path('order/razorpay_verify/<int:order_id>/', views.razorpay_verify, name='razorpay_verify'),
    path('order/failed/<int:order_id>/',views.order_failed,name='order_failed'),
    path('retry_payment/<int:order_id>/',views.retry_payment,name='retry_payment'),
]