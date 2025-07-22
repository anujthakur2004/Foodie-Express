from django.db import models
from datetime import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


STATUS_CHOICES = [
    ('received', 'Order Received'),
    ('preparing', 'Preparing'),
    ('baking', 'Baking/Cooking'),
    ('on_way', 'On the Way'),
    ('delivered', 'Delivered'),
    ]

class Category(models.Model):
    category_title = models.CharField(max_length=200)
    category_gif = models.CharField(max_length=200)
    category_description = models.TextField()

    def __str__(self):
        return f"{self.category_title}"




class Sub(models.Model):
    sub_filling = models.CharField(max_length=200)
    small_price = models.DecimalField(max_digits=6, decimal_places=2)
    large_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"Sub : {self.sub_filling}"

class Pasta(models.Model):
    dish_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.dish_name}"


class Salad(models.Model):
    dish_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"Salad : {self.dish_name}"

class Pizza(models.Model):
    dish_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.dish_name}"

class Rice(models.Model):
    dish_name = models.CharField(max_length=200)
    small_price = models.DecimalField(max_digits=6, decimal_places=2)
    large_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.dish_name}"

class UserOrder(models.Model):
    username = models.CharField(max_length=200)
    order = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    time_of_order = models.DateTimeField(default=datetime.now, blank=True)
    delivered = models.BooleanField()
    delivery_address = models.TextField(blank=True, null=True)  
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')

    def __str__(self):
        return f"Order placed by: {self.username} on {self.time_of_order.date()} at {self.time_of_order.time().strftime('%H:%M:%S')}"

class SavedCarts(models.Model):
    username = models.CharField(max_length=200, primary_key=True)
    cart = models.TextField()

    def __str__(self):
        return f"Saved cart for {self.username}"
    
class Biryani(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
    
class Rolls(models.Model):
    dish_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.dish_name}"

class Ni(models.Model):
    dish_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.dish_name}"

class Review(models.Model):
    name = models.CharField(max_length=100)
    rating = models.IntegerField()
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
