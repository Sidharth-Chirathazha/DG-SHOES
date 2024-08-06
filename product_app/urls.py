from django.urls import path,include
from . import views


urlpatterns = [

    path('product_list/',views.productList,name='product_list'),
    path('product_list/product_add/',views.addProduct,name="product_add"),
    path('product_list/variant_list/list_products/<int:color_image_id>/',views.list_products_view,name='list_products'),
    path('product_list/variant_list/unlist_products/<int:color_image_id>/',views.unlist_products_view,name="unlist_products"),
    path('product_list/product_edit/<int:product_id>/',views.editProduct,name='product_edit'),
    path('product_list/variant_list/<int:product_id>/',views.variant_list_view,name='variant_list'),
    path('product_list/variant_list/add_color_variant/<int:product_id>/',views.add_color_variant,name="add_color_variant"),
    path('product_list/variant_list/add_size_quantity/<int:color_image_id>/',views.add_size_quantity,name='add_size_quantity'),
    path('product_list/variant_list/edit_size_quantity/<int:color_image_id>/',views.edit_size_quantity,name='edit_size_quantity'),
    path('product_list/toggle_featured/<int:product_id>/',views.toggle_featured,name="toggle_featured"),
    path('product_list/apply_or_disable_offer_product/<int:product_id>/',views.apply_or_disable_offer_product,name='apply_or_disable_offer_product'),
 
]