from django.contrib import admin
from .models import Menu, SaleDetail, Sale

@admin.register(Menu)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']


@admin.register(Sale)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['sale_date', 'total_amount', 'payment_method', 'cash', 'change']


@admin.register(SaleDetail)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['sale', 'menu', 'quantity', 'price', 'subtotal']