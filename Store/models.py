from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
from django.core.validators import MinValueValidator



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=25, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
         return f"{self.user.username} | OTP: {self.otp or 'N/A'} | Verified: {'Yes' if self.is_verified else 'No'}"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Men Jackets', 'Men Jackets'),
        ('Women Jackets', 'Women Jackets'),
        ('Kids Jackets', 'Kids Jackets'),
        ('Men Shorts', 'Men Shorts'),
        ('Women Shorts', 'Women Shorts'),
        ('Men Caps', 'Men Caps'),
        ('Men Purse', 'Men Purse'),
        ('Women Purse', 'Women Purse'),
        ('Watch Straps', 'Watch Straps'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_discount_percentage(self):
        if self.discount_price and self.price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount, 1)
        return 0

    def get_final_price(self):
        return self.discount_price if self.discount_price else self.price
        
    def __str__(self):
        return self.name

    @property
    def category_slug(self):
        return self.category.lower().replace(' ', '-')

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username if self.user else 'Anonymous'}"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class CustomerDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField()
    country = models.CharField(max_length=100)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.full_name}"

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('jazzcash', 'JazzCash'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'Easypaisa'),
        ('paypal', 'PayPal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField()
    country = models.CharField(max_length=100)
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    shipping_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        try:
            # Convert string values to Decimal safely
            if self.total_amount:
                self.total_amount = Decimal(str(self.total_amount))
            if self.shipping_fee:
                self.shipping_fee = Decimal(str(self.shipping_fee))
            if self.tax_amount:
                self.tax_amount = Decimal(str(self.tax_amount))
            if self.subtotal:
                self.subtotal = Decimal(str(self.subtotal))
        except (InvalidOperation, TypeError):
            # Handle invalid decimal values
            if not self.total_amount:
                self.total_amount = Decimal('0.00')
            if not self.shipping_fee:
                self.shipping_fee = Decimal('0.00')
            if not self.tax_amount:
                self.tax_amount = Decimal('0.00')
            if not self.subtotal:
                self.subtotal = Decimal('0.00')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} by {self.full_name}"

    @property
    def customer_name(self):
        return self.full_name

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    def get_total(self):
        return self.price * self.quantity
