from django.urls import path, include
from .views import authView, home, contact, success

urlpatterns = [
    path("", home, name="home"),
    path('signup/', authView, name='authView'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('contact/', contact, name='contact'),
    path('success/', success, name='success')
]

