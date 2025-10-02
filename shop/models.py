from django.db import models
from django.contrib.auth.models import User

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    landmark = models.CharField(max_length=100, blank=True)
    save_for_future = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.full_name} ({self.city})"

# Create your models here.

from django.contrib import admin
from .models import UserAddress

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(UserAddress, on_delete=models.PROTECT)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, null=True, blank=True)
    offer = models.ForeignKey('Offer', on_delete=models.PROTECT, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        if self.product:
            return f"{self.product.title} x {self.quantity}"
        elif self.offer:
            return f"{self.offer.title} x {self.quantity}"
        else:
            return f"OrderItem x {self.quantity}"

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'city', 'state', 'pincode', 'created_at')
    search_fields = ('full_name', 'phone', 'city', 'state', 'pincode', 'user__username')
    list_filter = ('state', 'city', 'created_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity', 'subtotal')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address', 'total', 'status', 'created_at')
    search_fields = ('user__username', 'address__full_name', 'id')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    readonly_fields = ('user', 'address', 'subtotal', 'discount', 'total', 'created_at', 'updated_at')
    fields = ('user', 'address', 'subtotal', 'discount', 'total', 'status', 'created_at', 'updated_at')

# Remove standalone OrderItem admin registration for cleaner UI
# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('order', 'offer', 'price', 'quantity', 'subtotal')
#     search_fields = ('order__id', 'offer__title')

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_new = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True, help_text='Rating out of 5')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "description")

class Offer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    link = models.URLField(blank=True, null=True, help_text='Link to product or category (optional)')
    mrp = models.DecimalField(max_digits=10, decimal_places=2, help_text='Original price (MRP)', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Offer price', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=5, help_text='Product rating (1-5 stars)', null=True, blank=True)
    is_new = models.BooleanField(default=True, help_text='Show NEW badge', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "mrp", "is_active", "is_new", "created_at")
    search_fields = ("title", "description")
    list_filter = ("is_active", "is_new", "created_at")

class Contact(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
