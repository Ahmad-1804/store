from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Payment
from Store.models import Order

def process_payment(request, order_id):
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        payment_method = request.POST.get('payment_method')
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_amount,
        )
        
        # Handle different payment methods
        if payment_method in ['easypaisa', 'jazzcash']:
            return redirect('mobile_payment', payment_id=payment.id)
        elif payment_method in ['paypal', 'pakpay']:
            return redirect('online_payment', payment_id=payment.id)
        elif payment_method == 'credit_card':
            return redirect('card_payment', payment_id=payment.id)
        elif payment_method == 'cod':
            payment.payment_status = 'confirmed'
            payment.save()
            messages.success(request, 'Order placed successfully!')
            return redirect('order_confirmation')
            
    return redirect('checkout')
