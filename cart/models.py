from django.db import models
from django.utils import timezone

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    detail = models.CharField(max_length=1000)
    category = models.CharField(default=None, blank=True)

class Customer(models.Model):
    name = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    points = models.IntegerField(default=0)

class Promotion(models.Model):
    name = models.CharField(max_length=350)
    type = models.CharField(max_length=10)
    redeem_code = models.CharField(max_length=50)
    discount_rate = models.IntegerField(default=0)
    detail = models.CharField(max_length=1000)

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total_price = models.IntegerField(default=0)  # Optional: can be calculated dynamically

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    promotions = models.ManyToManyField(Promotion, default=None, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def calculate_total(self):
        return sum(item.total_price for item in self.items.all())