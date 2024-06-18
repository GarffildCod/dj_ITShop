"""
URL configuration for it_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from shop import views
from django.views.generic import TemplateView


urlpatterns = [
    
    path('fill_database/', views.fill_database, name='fill_database'),
    
    path('cart_page/', views.cart_page, name='cart_page'),
    path('category/', views.ProductsListView.as_view(), name='category'),

    # path('cart_view/',  
    #      TemplateView.as_view(template_name='shop/cart_page.html'), name='cart_view'),
    # path('detail/<int:pk>/',  
    #      TemplateView.as_view(template_name='shop/shop-details.html'), 
    #      name='shop_detail')
  
]
