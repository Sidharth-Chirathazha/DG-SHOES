from django.urls import path
from . import views


urlpatterns = [

    path('checkout/',views.checkout_view,name='checkout'),
    path('order_success/<int:order_id>/',views.order_success_view,name='order_success'),
    path('apply_coupon/',views.apply_coupon,name='apply_coupon'),
    path('remove_coupon/',views.remove_coupon,name='remove_coupon'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),

]