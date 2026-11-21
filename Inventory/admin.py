from django.contrib import admin
from .models import Item, Recipe, Inventory

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['menu', 'item', 'quantity_used']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity']