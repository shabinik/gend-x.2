from django.urls import path
from . import views


urlpatterns=[
   path('account/',views.my_account,name='my_account'),
   path('user_logout/',views.user_logout,name='user_logout'),
   path('add_address/',views.add_address,name='add_address'),
   path('display_address/',views.display_address,name='display_address'),
   path('delete_address/<int:id>',views.delete_address,name='delete_address'),
   path('edit_address/<int:id>',views.edit_address,name='edit_address'),
   path('change_password/',views.change_password,name='change_password'),
   path('edit/profile/<int:id>/',views.edit_profile,name='edit_profile'),
]