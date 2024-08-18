from django.urls import path,include
from . import views


urlpatterns = [

    path('user_account/',views.user_account_view,name='user_account'),
    path('update_user_info/',views.update_user_info,name='update_user_info'),
    path('add_address/',views.add_address,name='add_address'),
    path('edit_address/',views.edit_address,name='edit_address'),
    path('delete_address/<int:address_id>/',views.delete_address,name='delete_address'),
    path('get_address_details/',views.get_address_details,name='get_address_details'),
    path('change_password/', views.change_password,name='change_password'),
    path('cancel_order_item/<int:item_id>/',views.cancel_order_item,name='cancel_order_item'),
    path('return_order_item/<int:item_id>/',views.return_order_item,name='return_order_item'),
    path('order_details/<int:order_id>/',views.order_details,name='order_details'),
    path('retry-payment/<int:order_id>/', views.retry_payment, name='retry_payment'),
    path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),

]