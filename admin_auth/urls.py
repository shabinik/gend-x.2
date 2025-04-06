from django.urls import path
from . import views


urlpatterns=[
   path('admin',views.admin_login,name='admin_login'),
   path('home/',views.admin_home,name='admin_home'),
   path('logout_admin/',views.admin_logout,name='admin_logout'),
   path('users/',views.users_list,name='users_list'),
   path('block/<int:id>/',views.block_user,name='block_user'),
   path('download-report/<str:file_type>/', views.download_report, name='download_report'),
   path('sales_report/',views.sales_report,name='sales_report'),
   path('get-sales-data/', views.get_sales_data, name='get_sales_data'),
]
