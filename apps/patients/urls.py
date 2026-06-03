from django.urls import path

from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('create/', views.patient_form, name='patient_create'),
    path('<int:pk>/edit/', views.patient_form, name='patient_edit'),
    path('<int:pk>/delete/', views.patient_delete, name='patient_delete'),
]
