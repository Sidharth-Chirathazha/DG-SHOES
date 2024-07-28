from django.urls import path,include
from . import views


urlpatterns = [

    path('product_list/',views.productList,name='product_list'),
    path('product_add/',views.addProduct,name="product_add"),
    path('list_products/<int:color_image_id>/',views.list_products_view,name='list_products'),
    path('unlist_products/<int:color_image_id>/',views.unlist_products_view,name="unlist_products"),
    path('product_edit/<int:product_id>/',views.editProduct,name='product_edit'),
    path('variant_list/<int:product_id>/',views.variant_list_view,name='variant_list'),
    path('add_color_variant/<int:product_id>/',views.add_color_variant,name="add_color_variant"),
    path('add_size_quantity/<int:color_image_id>/',views.add_size_quantity,name='add_size_quantity'),
    path('edit_size_quantity/<int:color_image_id>/',views.edit_size_quantity,name='edit_size_quantity'),
    path('toggle_featured/<int:product_id>/',views.toggle_featured,name="toggle_featured"),
 
]