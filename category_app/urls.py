from django.urls import path,include
from . import views


urlpatterns = [

    path('category_list/',views.categoryList,name='category_list'),
    path('add_category/',views.addCategory,name='add_category'),
    # path('delete_category/<str:category_name>/',views.deleteCategory, name="delete_category"),
    path('subcategory_list/', views.subcategoryList,name='subcategory_list'),
    path('add_subcategory/',views.addSubCategory,name='add_subcategory'),
    path('unlist_subcategory/<int:category_id>/<int:subcategory_id>/',views.unlist_subcategory,name='unlist_subcategory'),
    path('list_subcategory/<int:category_id>/<int:subcategory_id>/',views.list_subcategory,name='list_subcategory')
 
]
