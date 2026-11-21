from decimal import Decimal
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrbean_System.settings")
django.setup()

from Inventory.models import Item, Recipe
from PoS.models import Menu

Recipe.objects.all().delete()

recipes_data = {
    "Strawberry Cocoa": {
        "Cocoa Powder": "15.00",
        "Strawberry Syrup": "25.00",
        "Fresh Milk": "0.18",
    },
    "Matcha Cocoa": {
        "Matcha Powder": "12.00",
        "Cocoa Powder": "12.00",
        "Fresh Milk": "0.18",
    },
    "Cold Whisk Matcha": {
        "Matcha Powder": "18.00",
        "Fresh Milk": "0.18",
    },
    "Cocoa Biscoff": {
        "Cocoa Powder": "15.00",
        "Fresh Milk": "0.15",
        "Biscoff Spread": "20.00",
    },
    "Oreo Cocoa": {
        "Cocoa Powder": "15.00",
        "Fresh Milk": "0.15",
        "Oreo cookies": "0.10",
    },
    "Dark Hour": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Dark Cocoa Powder": "20.00",
        "Caramel Syrup": "15.00",
    },
    "Dirty Matcha": {
        "Matcha Powder": "15.00",
        "Fresh Milk": "0.15",
        "Espresso Beans": "10.00",
    },
    "Nutella Latte": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Nutella": "25.00",
    },
    "Biscoff Latte": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Biscoff Spread": "20.00",
    },
    "Tiramisu Latte": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Tiramisu Syrup": "20.00",
    },
    "Affogato Latte": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Vanilla Ice Cream": "50.00",
    },
    "Caramel Macchiato": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Vanilla Extract": "5.00",
        "Caramel Syrup": "20.00",
    },
    "Salted Caramel": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Caramel Syrup": "20.00",
        "Sea Salt": "2.00",
        "Whipping Cream": "0.03",
    },
    "Caramel Latte": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Caramel Syrup": "25.00",
    },
    "Cafe Mocha": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Cocoa Powder": "20.00",
    },
    "Dark Mocha": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Dark Cocoa Powder": "20.00",
    },
    "Cafe Latte": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.18",
    },
    "Strawberry Cloud": {
        "Strawberry Syrup": "30.00",
        "Fresh Milk": "0.15",
        "Whipping Cream": "0.04",
    },
    "Matcha Biscoff": {
        "Matcha Powder": "15.00",
        "Fresh Milk": "0.15",
        "Biscoff Spread": "20.00",
    },
    "Oatcha": {
        "Matcha Powder": "15.00",
        "Oat Milk": "0.18",
    },
    "Matcha Latte": {
        "Matcha Powder": "15.00",
        "Fresh Milk": "0.18",
    },
    "Cocoa Cloud": {
        "Cocoa Powder": "20.00",
        "Fresh Milk": "0.15",
        "Whipping Cream": "0.04",
    },
    "Dark Cocoa": {
        "Dark Cocoa Powder": "20.00",
        "Fresh Milk": "0.18",
    },
    "Cocoa": {
        "Cocoa Powder": "20.00",
        "Fresh Milk": "0.18",
    },
    "Iced Milk Coffee": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
    },
    "Cinnamon Latte": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Cinnamon Powder": "5.00",
    },
    "Oat Latte": {
        "Espresso Beans": "10.00",
        "Oat Milk": "0.15",
    },
    "Vietnam Salt Coffee": {
        "Espresso Beans": "10.00",
        "Condensed Milk": "25.00",
        "Sea Salt": "2.00",
        "Whipping Cream": "0.03",
    },
    "Golden Hour": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "Caramel Syrup": "25.00",
        "Whipping Cream": "0.03",
    },
    "Spanish Latte": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.12",
        "Condensed Milk": "30.00",
    },
    "White Mocha": {
        "Espresso Beans": "10.00",
        "Fresh Milk": "0.15",
        "White Chocolate Syrup": "25.00",
    },
    "Americano": {
        "Espresso Beans": "10.00",
    },
}

for menu_name, ingredients in recipes_data.items():
    menu = Menu.objects.filter(name=menu_name).first()

    if not menu:
        print(f"Menu not found: {menu_name}")
        continue

    for item_name, qty in ingredients.items():
        item = Item.objects.filter(name=item_name).first()

        if not item:
            print(f"Item not found for {menu_name}: {item_name}")
            continue

        Recipe.objects.create(
            menu=menu,
            item=item,
            quantity_used=Decimal(qty)
        )

print("All recipes inserted successfully.")
print("Total recipes:", Recipe.objects.count())