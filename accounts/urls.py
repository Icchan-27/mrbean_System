from django.urls import path
from . import views

urlpatterns = [
    path("staff/", views.owner_staff, name="owner_staff"),
    path("add-staff/", views.add_staff, name="add_staff"),
    path("remove-staff/<int:user_id>/", views.remove_staff, name="remove_staff"),
]