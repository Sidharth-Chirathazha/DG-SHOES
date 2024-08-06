from django.urls import path
from . import views


urlpatterns = [

    path('coupons',views.coupons_view,name='coupons'),
    path('coupons/add_coupon',views.add_coupon,name='add_coupon'),
    path('coupons/edit_coupon/<int:coupon_id>/',views.edit_coupon,name='edit_coupon'),

]