from django.contrib import admin
from django.db.models import DecimalField
from django.forms import TextInput
from .models import Product, Cart, CartItem, CustomerDetails, Order, OrderItem, Profile

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

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
    list_display = ['id', 'full_name', 'phone', 'payment_method', 'get_total_amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'id']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']
    
    formfield_overrides = {
        DecimalField: {'widget': TextInput()},
    }

    def get_total_amount(self, obj):
        try:
            return round(float(obj.total_amount), 2) if obj.total_amount else 0.00
        except (ValueError, TypeError):
            return 0.00
    get_total_amount.short_description = 'Total Amount'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order',)

admin.site.register(Profile)
