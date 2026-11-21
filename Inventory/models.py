from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    menu = models.ForeignKey('PoS.Menu', on_delete=models.CASCADE, related_name='recipes')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='used_in_recipes')
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.menu.name} - {self.item.name}"

class Inventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} ({self.quantity})"