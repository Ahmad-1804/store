from django.db import models

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('easypaisa', 'Easypaisa'),
        ('jazzcash', 'JazzCash'),
        ('paypal', 'PayPal'),
        ('pakpay', 'PakPay'),
        ('credit_card', 'Credit/Debit Card'),
        ('cod', 'Cash on Delivery'),
    ]
    
    order = models.OneToOneField('Store.Order', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
