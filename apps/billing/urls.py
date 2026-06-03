from django.urls import path

from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('<int:pk>/print/', views.invoice_simple, name='invoice_simple'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('void/', views.invoice_void, name='invoice_void'),
]
