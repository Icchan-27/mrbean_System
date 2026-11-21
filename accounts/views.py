from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import UserProfile


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            profile = UserProfile.objects.filter(user=user).first()

            if profile is None:
                return redirect("management_dashboard")
            elif profile.role == "owner":
                return redirect("owner_home")
            else:
                return redirect("menu_page")

        return render(request, "registration/login.html", {
            "error": "Invalid username or password"
        })

    return render(request, "registration/login.html")


@login_required
def owner_staff(request):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.role != "owner":
        return redirect("menu_page")

    staffs = User.objects.filter(
        userprofile__role__in=["owner", "cashier"]
    ).exclude(
        id=request.user.id
    ).select_related("userprofile")

    return render(request, "ownerStaff.html", {
        "staffs": staffs,
    })


@login_required
def add_staff(request):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.role != "owner":
        return redirect("menu_page")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if role not in ["owner", "cashier"]:
            return redirect("owner_staff")

        if User.objects.filter(username=username).exists():
            return redirect("owner_staff")

        user = User.objects.create_user(
            username=username,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role=role
        )

    return redirect("owner_staff")


@login_required
def remove_staff(request, user_id):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.role != "owner":
        return redirect("menu_page")

    if request.method == "POST":
        user = User.objects.filter(
            id=user_id,
            userprofile__role__in=["owner", "cashier"]
        ).first()

        if user and user != request.user:
            user.delete()

    return redirect("owner_staff")