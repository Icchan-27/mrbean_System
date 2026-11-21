from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_page, name='menu_page'),
    path('sales/', views.dashboard_page, name='dashboard_page'),
    path('save-sale/', views.save_sale, name='save_sale'),
    path('sales-history/', views.dashboard2_page, name='dashboard2_page'),
    path('owner-home/', views.owner_home, name='owner_home'),
    path("owner-sales-history/", views.owner_sales_history, name="owner_sales_history"),
    path("owner-menu/", views.owner_menu, name="owner_menu"),
    path("add-menu/", views.add_menu, name="add_menu"),
    path("remove-menu/<int:menu_id>/", views.remove_menu, name="remove_menu"),
    path("edit-menu/", views.edit_menu, name="edit_menu"),
    path("paypal/create-order/", views.paypal_create_order, name="paypal_create_order"),
    path("paypal/capture-order/", views.paypal_capture_order, name="paypal_capture_order"),
]