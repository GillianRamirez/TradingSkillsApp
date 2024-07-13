from django.urls import path, include
from .views import authView, contact, success, navbar
from . import views



urlpatterns = [
    path("", views.ShareCommerce, name='home'),
    path('signup/', authView, name='authView'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('contact/', contact, name='contact'),
    path('success/', success, name='success'),
    path('navbar/', navbar, name='navbar'),
    path('sharegraph/', views.shareGraph, name="sharegraph"),
    path('assets/add_stock', views.add_stock, name="add_stock"),
    path('sell_stock/', views.sell_stock, name="sell_stock"),
     path('reset_portfolio/', views.reset_portfolio, name='reset_portfolio'),

]
