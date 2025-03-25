from django.contrib import admin
from .models import Product, Cart, CartItem, CustomerDetails, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_percentage', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'price', 'created_at')
    list_filter = ('created_at',)

@admin.register(CustomerDetails)
class CustomerDetailsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'country', 'order_total', 'created_at')
    list_filter = ('country', 'created_at')
    search_fields = ('full_name', 'email')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'email', 'payment_method', 'total_amount', 'created_at')
    list_filter = ('payment_method', 'created_at')
    search_fields = ('customer_name', 'email')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order',)
