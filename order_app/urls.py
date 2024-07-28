from django.urls import path
from . import views


urlpatterns = [

    path('checkout/',views.checkout_view,name='checkout'),
    path('order_success/<int:order_id>/',views.order_success_view,name='order_success'),

]