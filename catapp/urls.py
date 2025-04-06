from django.urls import path
from . import views


urlpatterns=[
    path('category/',views.category_list,name='category_list'),
    path('create/',views.create_category,name='create_category'),
    path('edit/<int:id>/',views.edit_category,name='edit_category'),
    path('unlist/<int:id>/',views.unlist_category,name='unlist_category'),
]