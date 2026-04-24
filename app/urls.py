from django.urls import path
from .  import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('create_customer/', views.create_customer, name='create_customer'),
    path('get_customers/', views.get_customers, name='get_customers'),
]