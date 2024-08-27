from django.urls import path,include
from . import views


urlpatterns = [

    path('dashboard/',views.dashboard,name='dashboard'),
    path('admin_login/',views.adminLogin,name='admin_login'),
    path('admin_logout/',views.adminLogout,name='admin_logout'),
    path('user_management/',views.user_management,name='user_management'),
    path('block_user/<int:user_id>/',views.block_user,name='block_user'),
    path('unblock_user/<int:user_id>/',views.unblock_user,name='unblock_user'),
    path('order_list/',views.orders_list,name='order_list'),
    path('confirm_order/<int:item_id>/',views.confirm_order,name='confirm_order'),
    path('return_order/<int:item_id>/',views.return_order,name='return_order'),
    path('change_order_status/<int:item_id>/', views.change_order_status, name='change_order_status'),
    path('order_info/<int:order_id>/',views.order_info,name='order_info'),
    path('dashboard/export_pdf/', views.export_pdf, name='export_pdf'),
    path('dashboard/export_excel/', views.export_excel, name='export_excel'),
    path('dashboard/sales_report/',views.sales_report,name='sales_report'),
    path('get_dashboard_data/', views.get_dashboard_data, name='get_dashboard_data'),
]
