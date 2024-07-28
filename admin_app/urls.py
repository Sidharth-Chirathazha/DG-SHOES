from django.urls import path,include
from . import views


urlpatterns = [

    path('dashboard/',views.dashboard,name='dashboard'),
    path('admin_login/',views.adminLogin,name='admin_login'),
    path('admin_reset_password/',views.forgot_admin_password,name='admin_reset_password'),
    path('admin_logout/',views.adminLogout,name='admin_logout'),
    path('user_management/',views.user_management,name='user_management'),
    path('block_user/<int:user_id>/',views.block_user,name='block_user'),
    path('unblock_user/<int:user_id>/',views.unblock_user,name='unblock_user'),
    path('order_list/',views.orders_list,name='order_list'),
    path('confirm_order/<int:item_id>/',views.confirm_order,name='confirm_order'),
    path('return_order/<int:item_id>/',views.return_order,name='return_order'),
    path('change_order_status/<int:item_id>/', views.change_order_status, name='change_order_status'),
    path('order_info/<int:order_id>/',views.order_info,name='order_info'),
]
