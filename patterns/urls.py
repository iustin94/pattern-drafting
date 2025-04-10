# patterns/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Measurement URLs
    path('measurements/', views.measurement_list, name='measurement_list'),
    path('measurements/new/', views.measurement_create, name='measurement_create'),
    path('measurements/<int:pk>/edit/', views.measurement_update, name='measurement_update'),
    path('measurements/<int:pk>/delete/', views.measurement_delete, name='measurement_delete'),

    # Pattern URLs
    path('', views.pattern_list, name='pattern_list'),
    path('new/', views.pattern_create, name='pattern_create'),
    path('<int:pk>/', views.pattern_detail, name='pattern_detail'),
    path('<int:pk>/delete/', views.pattern_delete, name='pattern_delete'),
    path('<int:pk>/pdf/', views.download_pdf, name='download_pdf'),
    path('<int:pk>/svg/<int:piece_id>/', views.download_svg, name='download_svg'),
]