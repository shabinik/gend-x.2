from django.urls import path
from . import views


urlpatterns=[
   path('create_product/',views.create_product,name='create_product'),
   path('list_product/',views.product_list,name='product_list'),
   path('unlist_product/<int:id>/',views.product_unlist,name='product_unlist'),
   path('edit_product/<int:id>/',views.edit_product,name='edit_product'),
   path('list_varients/<int:id>/',views.list_varient,name='list_varient'),
   path('create_varient/<int:id>',views.create_varient,name='create_varient'),
   path('edit_varient/<int:id>/<int:varient_id>/',views.edit_varient,name='edit_varient')
]
