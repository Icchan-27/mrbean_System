from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from .models import Inventory, Item


@login_required
@never_cache
def owner_inventory(request):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.role != "owner":
        return redirect("menu_page")

    inventories = Inventory.objects.select_related("item").all()
    inventory_map = {inv.item_id: inv.quantity for inv in inventories}

    items_for_edit = []
    for item in Item.objects.all():
        items_for_edit.append({
            "id": item.id,
            "name": item.name,
            "quantity": inventory_map.get(item.id, ""),
        })

    return render(request, "ownerInventory.html", {
        "inventories": inventories,
        "items_for_edit": items_for_edit,
    })


@login_required
@never_cache
def add_inventory(request):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.role != "owner":
        return redirect("menu_page")

    if request.method == "POST":
        name = request.POST.get("name")
        unit = request.POST.get("unit")
        quantity = request.POST.get("quantity")
        description = request.POST.get("description", "")

        if name and unit and quantity:
            item = Item.objects.create(
                name=name,
                unit=unit,
                description=description,
            )

            Inventory.objects.create(
                item=item,
                quantity=quantity,
            )

    return redirect("owner_inventory")


@login_required
@never_cache
def edit_inventory(request):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.role != "owner":
        return redirect("menu_page")

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        name = request.POST.get("name")
        quantity = request.POST.get("quantity")

        item = get_object_or_404(Item, id=item_id)

        if name:
            item.name = name
            item.save()

        inventory, created = Inventory.objects.get_or_create(
            item=item,
            defaults={"quantity": 0}
        )

        if quantity:
            inventory.quantity = quantity
            inventory.save()

    return redirect("owner_inventory")


@login_required
@never_cache
def remove_inventory(request, id):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.role != "owner":
        return redirect("menu_page")

    if request.method == "POST":
        inventory = get_object_or_404(Inventory, id=id)
        item = inventory.item
        inventory.delete()
        item.delete()

    return redirect("owner_inventory")

@login_required
@never_cache
def staff_inventory(request):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.role != "cashier":
        return redirect("menu_page")

    inventories = Inventory.objects.select_related("item").all()

    return render(request, "staffInventory.html", {
        "inventories": inventories,
    })