import json
import base64
import requests
from decimal import Decimal
from collections import OrderedDict
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.timezone import localdate
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from Inventory.models import Item, Recipe, Inventory
from .models import Menu, Sale, SaleDetail


def get_menu_stock_status(menu):
    recipes = Recipe.objects.select_related("item").filter(menu=menu)

    if not recipes.exists():
        return "ok", ""

    for recipe in recipes:
        inventory = Inventory.objects.filter(item=recipe.item).first()
        available = inventory.quantity if inventory else Decimal("0")
        needed = recipe.quantity_used

        if available < needed:
            return "not_enough", f"Not enough {recipe.item.name}"

    for recipe in recipes:
        inventory = Inventory.objects.filter(item=recipe.item).first()
        available = inventory.quantity if inventory else Decimal("0")
        needed = recipe.quantity_used

        if needed > 0:
            servings_left = available / needed
            if servings_left <= 5:
                return "low", f"Low on {recipe.item.name}"

    return "ok", ""


@login_required
@never_cache
def edit_menu(request):
    if request.method == "POST":
        menu_id = request.POST.get("menu_id")
        new_price = request.POST.get("menu_price")

        menu = Menu.objects.filter(id=menu_id).first()

        if menu:
            menu.price = new_price
            menu.save()

    return redirect("owner_menu")


@login_required
@never_cache
def owner_menu(request):
    if request.user.userprofile.role != "owner":
        return redirect("menu_page")

    menus = Menu.objects.all()
    items = Item.objects.all()

    menus_with_status = []
    for menu in menus:
        stock_status, stock_message = get_menu_stock_status(menu)
        menus_with_status.append({
            "id": menu.id,
            "name": menu.name,
            "price": menu.price,
            "description": menu.description,
            "stock_status": stock_status,
            "stock_message": stock_message,
        })

    return render(request, "ownerMenu.html", {
        "menus": menus_with_status,
        "items": items,
    })


@login_required
@never_cache
def add_menu(request):
    if request.user.userprofile.role != "owner":
        return redirect("menu_page")

    if request.method == "POST":
        menu_name = request.POST.get("menu_name")
        menu_price = request.POST.get("menu_price")
        item_ids = request.POST.getlist("item_ids[]")
        quantities = request.POST.getlist("quantities[]")

        if menu_name and menu_price:
            menu = Menu.objects.create(
                name=menu_name,
                price=Decimal(menu_price),
            )

            for item_id, qty in zip(item_ids, quantities):
                if item_id and qty:
                    Recipe.objects.create(
                        menu=menu,
                        item=Item.objects.get(id=item_id),
                        quantity_used=Decimal(qty),
                    )

    return redirect("owner_menu")


@login_required
@never_cache
def remove_menu(request, menu_id):
    if request.user.userprofile.role != "owner":
        return redirect("menu_page")

    if request.method == "POST":
        menu = Menu.objects.filter(id=menu_id).first()
        if menu:
            menu.delete()

    return redirect("owner_menu")


@login_required
@never_cache
def menu_page(request):
    menus = Menu.objects.all()

    menus_with_status = []
    for menu in menus:
        stock_status, stock_message = get_menu_stock_status(menu)
        menus_with_status.append({
            "id": menu.id,
            "name": menu.name,
            "price": menu.price,
            "description": menu.description,
            "stock_status": stock_status,
            "stock_message": stock_message,
        })

    return render(request, "menu.html", {
        "menus": menus_with_status,
    })


@login_required
@never_cache
def dashboard_page(request):
    today = localdate()

    today_sales = Sale.objects.filter(sale_date__date=today)

    total_sales = today_sales.aggregate(total=Sum("total_amount"))["total"] or 0
    orders_today = today_sales.count()

    product_sales_qs = (
        SaleDetail.objects
        .filter(sale__sale_date__date=today)
        .values("menu__name")
        .annotate(
            sales=Sum("quantity"),
            amount=Sum("subtotal"),
        )
        .order_by("-amount")
    )

    product_sales = [
        {
            "name": item["menu__name"],
            "sales": item["sales"] or 0,
            "amount": item["amount"] or 0,
        }
        for item in product_sales_qs
    ]

    top_item = product_sales[0]["name"] if product_sales else "-"

    return render(request, "dashboard.html", {
        "product_sales": json.dumps(product_sales),
        "product_sales_list": product_sales,
        "total_sales": total_sales,
        "orders_today": orders_today,
        "top_item": top_item,
    })


@login_required
@never_cache
def dashboard2_page(request):
    today = localdate()

    sales_today = Sale.objects.filter(
        sale_date__date=today
    ).order_by("-sale_date")

    transactions = []

    for sale in sales_today:
        details = SaleDetail.objects.filter(sale=sale).select_related("menu")

        order_details = [
            f"{detail.menu.name} x{detail.quantity}"
            for detail in details
        ]

        transactions.append({
            "date_time": sale.sale_date,
            "order_number": sale.id,
            "order_details": order_details,
            "total": sale.total_amount,
            "payment": sale.payment_method,
            "staff": sale.cashier.username if sale.cashier else "Unknown",
        })

    return render(request, "dashboard2.html", {
        "today": today.strftime("%B %d, %Y"),
        "transactions": transactions,
    })


@login_required
@never_cache
def owner_home(request):
    if request.user.userprofile.role != "owner":
        return redirect("menu_page")

    period = request.GET.get("period", "today")
    today = localdate()

    if period == "weekly":
        start_date = today - timedelta(days=6)
        end_date = today
        chart_type = "line"
    elif period == "monthly":
        start_date = today.replace(day=1)
        end_date = today
        chart_type = "line"
    elif period == "yearly":
        start_date = today.replace(month=1, day=1)
        end_date = today
        chart_type = "line"
    else:
        period = "today"
        start_date = today
        end_date = today
        chart_type = "donut"

    sales_qs = Sale.objects.filter(
        sale_date__date__range=[start_date, end_date]
    )

    total_sales = sales_qs.aggregate(total=Sum("total_amount"))["total"] or 0
    orders_count = sales_qs.count()

    product_sales_qs = (
        SaleDetail.objects
        .filter(sale__sale_date__date__range=[start_date, end_date])
        .values("menu__name")
        .annotate(
            sales=Sum("quantity"),
            amount=Sum("subtotal"),
        )
        .order_by("-sales", "-amount")
    )

    product_sales = [
        {
            "name": item["menu__name"],
            "sales": item["sales"] or 0,
            "amount": item["amount"] or 0,
        }
        for item in product_sales_qs
    ]

    top_item = product_sales[0]["name"] if product_sales else "-"

    line_labels = []
    line_values = []

    if period == "weekly":
        grouped = (
            sales_qs
            .annotate(group_date=TruncDate("sale_date"))
            .values("group_date")
            .annotate(total=Sum("total_amount"))
            .order_by("group_date")
        )

        totals_by_day = OrderedDict()
        for i in range(7):
            day = start_date + timedelta(days=i)
            totals_by_day[day.strftime("%b %d")] = 0

        for row in grouped:
            label = row["group_date"].strftime("%b %d")
            totals_by_day[label] = row["total"] or 0

        line_labels = list(totals_by_day.keys())
        line_values = list(totals_by_day.values())

    elif period == "monthly":
        grouped = (
            sales_qs
            .annotate(group_date=TruncDate("sale_date"))
            .values("group_date")
            .annotate(total=Sum("total_amount"))
            .order_by("group_date")
        )

        totals_by_day = OrderedDict()
        current_day = start_date

        while current_day <= end_date:
            totals_by_day[current_day.strftime("%b %d")] = 0
            current_day += timedelta(days=1)

        for row in grouped:
            label = row["group_date"].strftime("%b %d")
            totals_by_day[label] = row["total"] or 0

        line_labels = list(totals_by_day.keys())
        line_values = list(totals_by_day.values())

    elif period == "yearly":
        grouped = (
            sales_qs
            .annotate(group_month=TruncMonth("sale_date"))
            .values("group_month")
            .annotate(total=Sum("total_amount"))
            .order_by("group_month")
        )

        month_names = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]

        totals_by_month = OrderedDict((month, 0) for month in month_names)

        for row in grouped:
            month_label = row["group_month"].strftime("%b")
            totals_by_month[month_label] = row["total"] or 0

        line_labels = list(totals_by_month.keys())
        line_values = list(totals_by_month.values())

    period_labels = {
        "today": "Today",
        "weekly": "This Week",
        "monthly": "This Month",
        "yearly": "This Year",
    }

    return render(request, "ownerhomepage.html", {
        "product_sales": json.dumps(product_sales),
        "product_sales_list": product_sales,
        "total_sales": total_sales,
        "orders_count": orders_count,
        "top_item": top_item,
        "period": period,
        "period_label": period_labels[period],
        "chart_type": chart_type,
        "line_labels": json.dumps(line_labels),
        "line_values": json.dumps(line_values),
    })


@login_required
@never_cache
def owner_sales_history(request):
    if request.user.userprofile.role != "owner":
        return redirect("menu_page")

    selected_date = request.GET.get("date")
    today = localdate()

    if selected_date:
        from datetime import datetime
        try:
            filter_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        except ValueError:
            filter_date = today
    else:
        filter_date = today

    sales_qs = Sale.objects.filter(
        sale_date__date=filter_date
    ).order_by("-sale_date")

    transactions = []

    for sale in sales_qs:
        details = SaleDetail.objects.filter(sale=sale).select_related("menu")

        order_details = [
            f"{detail.menu.name} x{detail.quantity}"
            for detail in details
        ]

        transactions.append({
            "date_time": sale.sale_date,
            "order_number": sale.id,
            "order_details": order_details,
            "total": sale.total_amount,
            "payment": sale.payment_method,
            "staff": sale.cashier.username if sale.cashier else "Unknown",
        })

    return render(request, "ownerSalesHistory.html", {
        "selected_date": filter_date.strftime("%Y-%m-%d"),
        "display_date": filter_date.strftime("%B %d, %Y"),
        "transactions": transactions,
    })


def build_sale_data(cart):
    total_amount = Decimal("0")
    cart_items = []
    required_ingredients = {}

    for item in cart:
        menu = Menu.objects.get(id=item["id"])
        quantity = int(item["quantity"])
        price = menu.price
        subtotal = price * quantity

        total_amount += subtotal
        cart_items.append({
            "menu": menu,
            "quantity": quantity,
            "price": price,
            "subtotal": subtotal,
        })

        recipes = Recipe.objects.select_related("item").filter(menu=menu)

        for recipe in recipes:
            needed = recipe.quantity_used * quantity

            if recipe.item_id in required_ingredients:
                required_ingredients[recipe.item_id]["needed"] += needed
            else:
                required_ingredients[recipe.item_id] = {
                    "item": recipe.item,
                    "needed": needed,
                }

    return total_amount, cart_items, required_ingredients


def validate_inventory(required_ingredients):
    for item_id, data_needed in required_ingredients.items():
        inventory = Inventory.objects.filter(item_id=item_id).first()
        available = inventory.quantity if inventory else Decimal("0")

        if available < data_needed["needed"]:
            return data_needed["item"].name

    return None


def create_sale_and_deduct_inventory(user, cart, payment_method, cash=None, change=None):
    total_amount, cart_items, required_ingredients = build_sale_data(cart)

    lacking_item = validate_inventory(required_ingredients)
    if lacking_item:
        raise ValueError(f"Not enough {lacking_item}.")

    sale = Sale.objects.create(
        cashier=user,
        total_amount=total_amount,
        payment_method=payment_method,
        cash=cash,
        change=change,
    )

    for item in cart_items:
        SaleDetail.objects.create(
            sale=sale,
            menu=item["menu"],
            quantity=item["quantity"],
            price=item["price"],
            subtotal=item["subtotal"],
        )

    for item_id, data_needed in required_ingredients.items():
        inventory = Inventory.objects.filter(item_id=item_id).first()
        inventory.quantity -= data_needed["needed"]
        inventory.save()

    return sale, total_amount


@login_required
@require_POST
def save_sale(request):
    try:
        data = json.loads(request.body)

        cart = data.get("cart", [])
        payment_method = data.get("payment_method")
        cash = data.get("cash")

        if not cart:
            return JsonResponse(
                {"success": False, "message": "Cart is empty."},
                status=400
            )

        total_amount, _, required_ingredients = build_sale_data(cart)

        lacking_item = validate_inventory(required_ingredients)
        if lacking_item:
            return JsonResponse(
                {"success": False, "message": f"Not enough {lacking_item}."},
                status=400
            )

        if payment_method == "Cash":
            cash = int(cash or 0)

            if cash < total_amount:
                return JsonResponse(
                    {"success": False, "message": "Cash is not enough."},
                    status=400
                )

            change = cash - total_amount
            sale, _ = create_sale_and_deduct_inventory(
                request.user,
                cart,
                "Cash",
                cash=cash,
                change=change,
            )
        else:
            sale, _ = create_sale_and_deduct_inventory(
                request.user,
                cart,
                payment_method,
                cash=None,
                change=None,
            )

        return JsonResponse({
            "success": True,
            "sale_id": sale.id
        })

    except Menu.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "One or more menu items do not exist."},
            status=404
        )
    except ValueError as e:
        return JsonResponse(
            {"success": False, "message": str(e)},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": str(e)},
            status=500
        )


def get_paypal_access_token():
    auth = base64.b64encode(
        f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode()
    ).decode()

    response = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"},
        timeout=30,
    )

    token_data = response.json()

    if response.status_code != 200:
        raise Exception(token_data.get("error_description", "Failed to get PayPal access token."))

    return token_data["access_token"]


@login_required
@require_POST
def paypal_create_order(request):
    try:
        data = json.loads(request.body)
        cart = data.get("cart", [])

        if not cart:
            return JsonResponse(
                {"success": False, "message": "Cart is empty."},
                status=400
            )

        total_amount, _, required_ingredients = build_sale_data(cart)

        lacking_item = validate_inventory(required_ingredients)
        if lacking_item:
            return JsonResponse(
                {"success": False, "message": f"Not enough {lacking_item}."},
                status=400
            )

        token = get_paypal_access_token()

        response = requests.post(
            "https://api-m.sandbox.paypal.com/v2/checkout/orders",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "PHP",
                        "value": str(total_amount)
                    }
                }]
            },
            timeout=30,
        )

        paypal_data = response.json()

        if response.status_code not in [200, 201]:
            return JsonResponse(
                {
                    "success": False,
                    "message": paypal_data.get("message", "PayPal failed"),
                    "paypal": paypal_data
                },
                status=400
            )

        return JsonResponse(paypal_data)

    except Menu.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "One or more menu items do not exist."},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": str(e)},
            status=500
        )


@login_required
@require_POST
def paypal_capture_order(request):
    try:
        data = json.loads(request.body)
        order_id = data.get("orderID")
        cart = data.get("cart", [])

        if not order_id:
            return JsonResponse(
                {"success": False, "message": "Missing PayPal order ID."},
                status=400
            )

        if not cart:
            return JsonResponse(
                {"success": False, "message": "Cart is empty."},
                status=400
            )

        token = get_paypal_access_token()

        response = requests.post(
            f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30,
        )

        paypal_data = response.json()

        if response.status_code not in [200, 201]:
            return JsonResponse(
                {
                    "success": False,
                    "message": paypal_data.get("message", "PayPal capture failed"),
                    "paypal": paypal_data
                },
                status=400
            )

        if paypal_data.get("status") != "COMPLETED":
            return JsonResponse(
                {"success": False, "message": "Payment not completed."},
                status=400
            )

        sale, _ = create_sale_and_deduct_inventory(
            request.user,
            cart,
            "PayPal",
            cash=None,
            change=None,
        )

        return JsonResponse({
            "success": True,
            "status": "COMPLETED",
            "sale_id": sale.id
        })

    except Menu.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "One or more menu items do not exist."},
            status=404
        )
    except ValueError as e:
        return JsonResponse(
            {"success": False, "message": str(e)},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": str(e)},
            status=500
        )