from django.urls import path,include
from . import views


urlpatterns = [

    path('',views.indexPage,name='index'),
    path('login/',views.loginPage,name='login'),
    path('home/',views.homePage,name='home'),
    path('register/',views.registerPage,name='register'),
    path('logout/',views.logoutView,name='logout'),
    path('otp_verification/',views.otpVerification,name='otp_verification'),
    path('resend_otp/',views.resendOtp,name="resend_otp"),
    path('forgot_password/',views.forgotPassword,name='forgot_password'),
    path('verify_password/',views.verifyPassword,name='verify_password'),
    path('shop_list/',views.shopList,name='shop_list'),
    path('product_detail/<int:pk>/',views.product_detail_view,name='product_detail'),
    path('contact_us/',views.contactUs,name='contact_us'),

]