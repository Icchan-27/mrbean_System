from django.urls import path
from . import views

urlpatterns = [
    path('', views.management_dashboard, name='management_dashboard'),

    path('users/', views.management_users, name='management_users'),
    path('users/add/', views.management_add_user, name='management_add_user'),
    path('users/edit/<int:user_id>/', views.management_edit_user, name='management_edit_user'),
    path('users/remove/<int:user_id>/', views.management_remove_user, name='management_remove_user'),

    path('menu/', views.management_menu, name='management_menu'),
    path('menu/add/', views.management_add_menu, name='management_add_menu'),
    path('menu/edit/<int:menu_id>/', views.management_edit_menu, name='management_edit_menu'),
    path('menu/remove/<int:menu_id>/', views.management_remove_menu, name='management_remove_menu'),

    path('inventory/', views.management_inventory, name='management_inventory'),
    path('inventory/add/', views.management_add_inventory, name='management_add_inventory'),
    path('inventory/edit/<int:inv_id>/', views.management_edit_inventory, name='management_edit_inventory'),
    path('inventory/remove/<int:inv_id>/', views.management_remove_inventory, name='management_remove_inventory'),

    path('sales/', views.management_sales, name='management_sales'),
]