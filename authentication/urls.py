"""
URL configuration for it_website project.
"""
from django.contrib import admin
from django.urls import include, path
from authentication import views


urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('register/',views.RegisterView.as_view(), name='register'),
    path('logout/',views.logout_user, name='logout'),
]
