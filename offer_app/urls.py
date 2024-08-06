from django.urls import path,include
from . import views


urlpatterns = [

    path('offers/',views.offers_view,name='offers'),
    path('offers/add_offer',views.add_offer,name='add_offer'),
    path('offers/edit_offer',views.edit_offer,name='edit_offer'),
    path('offers/delete_offer',views.delete_offer,name='delete_offer'),
    path('api/offer/<int:offer_id>/', views.get_offer, name='get_offer'),

]