from django.urls import path,include
from . import views


urlpatterns = [

    path('sample/',views.sample,name="sample"),

]