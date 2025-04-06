from django.urls import path
from . import views


urlpatterns=[
    path('transactions/',views.transactions_list,name='transactions_list'),
]
   