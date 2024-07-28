from django.urls import path
from . import views


urlpatterns = [

    path('cart_detail/',views.cart_view,name='cart_detail'),
    path('add_to_cart/',views.add_to_cart,name='add_to_cart'),
    path('update_cart_item_quantity/',views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('delete_cart_item/s<int:item_id>/',views.delete_cart_item,name='delete_cart_item'),
    path('clear_cart/',views.clear_cart,name='clear_cart'),
    path('wishlist/',views.wishlist_view,name='wishlist'),
    path('add_to_wishlist/<int:product_variant_id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('add_to_cart_from_wishlist/<int:wishlist_item_id>/',views.add_to_cart_from_wishlist,name='add_to_cart_from_wishlist'),
    path('add_all_items_to_cart/',views.add_all_items_to_cart,name='add_all_items_to_cart'),
    path('clear_wishlist/',views.clear_wishlist,name='clear_wishlist'),
    path('remove_wishlist_item/<int:wishlist_item_id>/',views.remove_wishlist_item,name='remove_wishlist_item'),

]