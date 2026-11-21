from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.utils.timezone import localdate
from django.views.decorators.cache import never_cache

from accounts.models import UserProfile
from PoS.models import Menu, Sale
from Inventory.models import Item, Inventory


def can_access_management(user):
    profile = getattr(user, "userprofile", None)
    return profile is None or profile.role == "owner"


@login_required
@never_cache
def management_dashboard(request):
    if not can_access_management(request.user):
        return redirect("menu_page")

    today = localdate()

    total_users = User.objects.count()
    total_owners = UserProfile.objects.filter(role="owner").count()
    total_cashiers = UserProfile.objects.filter(role="cashier").count()
    total_menu_items = Menu.objects.count()
    total_inventory_items = Inventory.objects.count()
    sales_today = Sale.objects.filter(sale_date__date=today).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    return render(request, "management/dashboard.html", {
        "total_users": total_users,
        "total_owners": total_owners,
        "total_cashiers": total_cashiers,
        "total_menu_items": total_menu_items,
        "total_inventory_items": total_inventory_items,
        "sales_today": sales_today,
    })


@login_required
@never_cache
def management_users(request):
    if not can_access_management(request.user):
        return redirect("menu_page")

    users = User.objects.all().order_by("id").select_related("userprofile")

    return render(request, "management/users.html", {
        "users": users
    })


@login_required
@never_cache
def management_add_user(request):
    if not can_access_management(request.user):
        return redirect("menu_page")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        role = request.POST.get("role", "").strip()

        if username and password:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password=password
                )

                if role in ["owner", "cashier"]:
                    UserProfile.objects.create(
                        user=user,
                        role=role
                    )

    return redirect("management_users")


@login_required
@never_cache
def management_edit_user(request, user_id):
    if not can_access_management(request.user):
        return redirect("menu_page")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        role = request.POST.get("role", "").strip()

        if username:
            exists = User.objects.filter(username=username).exclude(id=user.id).exists()
            if not exists:
                user.username = username
                user.save()

        profile = getattr(user, "userprofile", None)

        if role in ["owner", "cashier"]:
            if profile:
                profile.role = role
                profile.save()
            else:
                UserProfile.objects.create(user=user, role=role)
        else:
            if profile:
                profile.delete()

    return redirect("management_users")


@login_required
@never_cache
def management_remove_user(request, user_id):
    if not can_access_management(request.user):
        return redirect("menu_page")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        if user != request.user:
            user.delete()

    return redirect("management_users")


@login_required
@never_cache
def management_menu(request):
    if not can_access_management(request.user):
        return redirect("menu_page")

    menus = Menu.objects.all().order_by("id")

    return render(request, "management/menu.html", {
        "menus": menus
    })


@login_required
@never_cache
def management_add_menu(request):
    if not can_access_management(request.user):
        return redirect("menu_page")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price", "").strip()
        image = request.FILES.get("image")

        if name and price:
            menu = Menu(
                name=name,
                price=price,
            )

            if hasattr(menu, "image") and image:
                menu.image = image

            menu.save()

    return redirect("management_menu")


@login_required
@never_cache
def management_edit_menu(request, menu_id):
    if not can_access_management(request.user):
        return redirect("menu_page")

    menu = get_object_or_404(Menu, id=menu_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price", "").strip()
        image = request.FILES.get("image")

        if name:
            menu.name = name

        if price:
            menu.price = price

        if hasattr(menu, "image") and image:
            menu.image = image

        menu.save()

    return redirect("management_menu")


@login_required
@never_cache
def management_remove_menu(request, menu_id):
    if not can_access_management(request.user):
        return redirect("menu_page")

    menu = get_object_or_404(Menu, id=menu_id)

    if request.method == "POST":
        menu.delete()

    return redirect("management_menu")


@login_required
@never_cache
def management_inventory(request):
    if not can_access_management(request.user):
        return redirect("menu_page")

    inventories = Inventory.objects.select_related("item").all().order_by("id")

    return render(request, "management/inventory.html", {
        "inventories": inventories
    })


@login_required
@never_cache
def management_add_inventory(request):
    if not can_access_management(request.user):
        return redirect("menu_page")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        unit = request.POST.get("unit", "").strip()
        quantity = request.POST.get("quantity", "").strip()

        if name and unit:
            item = Item.objects.create(
                name=name,
                unit=unit
            )

            Inventory.objects.create(
                item=item,
                quantity=quantity or 0
            )

    return redirect("management_inventory")


@login_required
@never_cache
def management_edit_inventory(request, inv_id):
    if not can_access_management(request.user):
        return redirect("menu_page")

    inv = get_object_or_404(Inventory, id=inv_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        unit = request.POST.get("unit", "").strip()
        quantity = request.POST.get("quantity", "").strip()

        if name:
            inv.item.name = name

        if unit:
            inv.item.unit = unit

        if quantity != "":
            inv.quantity = quantity

        inv.item.save()
        inv.save()

    return redirect("management_inventory")


@login_required
@never_cache
def management_remove_inventory(request, inv_id):
    if not can_access_management(request.user):
        return redirect("menu_page")

    inv = get_object_or_404(Inventory, id=inv_id)

    if request.method == "POST":
        inv.item.delete()

    return redirect("management_inventory")


@login_required
@never_cache
def management_sales(request):
    if not can_access_management(request.user):
        return redirect("menu_page")

    sales = Sale.objects.all().order_by("-sale_date")

    return render(request, "management/sales.html", {
        "sales": sales
    })