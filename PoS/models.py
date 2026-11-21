from django.db import models
from django.contrib.auth.models import User

class Menu(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='menu/', null=True, blank=True)
    
    def __str__(self):
        return self.name


class Sale(models.Model):
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.IntegerField()
    payment_method = models.CharField(max_length=50)
    cash = models.IntegerField(null=True, blank=True)
    change = models.IntegerField(null=True, blank=True)


class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    subtotal = models.IntegerField()