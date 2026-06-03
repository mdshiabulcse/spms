from django.urls import path

from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('create/', views.appointment_create, name='appointment_create'),
    path('<int:pk>/status/', views.appointment_status_update, name='appointment_status_update'),
]
