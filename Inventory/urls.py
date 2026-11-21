from django.urls import path
from . import views

urlpatterns = [
    path("owner/", views.owner_inventory, name="owner_inventory"),
    path("add/", views.add_inventory, name="add_inventory"),
    path("edit/", views.edit_inventory, name="edit_inventory"),
    path("remove/<int:id>/", views.remove_inventory, name="remove_inventory"),
    path("staff/", views.staff_inventory, name="staff_inventory"),
]