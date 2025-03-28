from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse  # Add this import
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Order, OrderItem, Profile
import random
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
import hashlib
import datetime
import requests





MERCHANT_ID = 'MC147369'
PASSWORD = '5u040f9g2x'
INTEGRITY_SALT = '432tz9622y'
RETURN_URL = 'https://yourdomain.com/payment/callback/'
JAZZCASH_BASE_URL = 'https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform/'
RETURN_URL = 'https://yourdomain.com/payment/callback/'
JAZZCASH_BASE_URL = 'https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform/'

# Function to generate JazzCash secure hash
def generate_secure_hash(data_dict):
    sorted_data = "&".join(f"{key}={value}" for key, value in sorted(data_dict.items()))
    hash_string = INTEGRITY_SALT + "&" + sorted_data
    return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()


# Add this helper function at the top of the file
def get_cart_count(request):
    """Helper function to get the number of items in the cart"""
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user).count()
    return 0

def admin_dashboard(request):
    return render(request, 'Store/admin_dashboard.html')
 
def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if any of the fields are empty
        if not username or not email or not password:
            return render(request, 'store/register.html', {'error': 'All fields are required'})

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'store/register.html', {'error': 'Username already exists'})
        if User.objects.filter(email=email).exists():
            return render(request, 'store/register.html', {'error': 'Email already exists'})

        # Create the user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            otp = str(random.randint(1000, 9999))
            Profile.objects.create(user=user, otp=otp)

            send_mail(
                'Leather Store - Email Verification',  # Updated subject with Leather Store
                f'Your OTP for Leather Store is: {otp}',  # Updated message with Leather Store
                'noreply@leatherstore.com',  # Updated sender email
                [email],
            )
            return render(request, 'store/verify.html', {'username': username, 'message': 'OTP sent to your email'})

        except Exception as e:
            return render(request, 'store/register.html', {'error': f'Error: {str(e)}'})

    return render(request, 'store/register.html')


def verify_email(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        otp = request.POST.get('otp')

        try:
            # Fetch the Profile associated with the username
            profile = Profile.objects.get(user__username=username)

            # Check if the OTP matches
            if profile.otp == otp:
                profile.is_verified = True
                profile.save()  # Corrected this line: you need to save the profile to update the verification status

                # Log the user in automatically after successful OTP verification
                user = profile.user  # Get the user object associated with the profile
                login(request, user)  # Log the user in

                # Redirect to the home page or dashboard after successful verification and login
                return redirect('home_page')
            else:
                # If OTP is incorrect, show an error message
                return render(request, 'store/verify.html', {
                    'username': username,
                    'otp': otp,
                    'error': 'Invalid OTP'
                })
        except Profile.DoesNotExist:
            # If Profile doesn't exist, show an error message
            return render(request, 'store/verify.html', {'error': 'User not found'})

    return redirect('register')  # If it's not a POST request, redirect to the register page
 
 
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"trying to login: {username} and this is a {password}")
        
        try:
            user = User.objects.get(username=username)  # Find user by email
            username = user.username  # Get username for authentication
        except User.DoesNotExist:
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})
        
        
        user = authenticate(request, username=username, password=password)
        print(f"Authenticated User: {user}")    
        
        if user:
            if hasattr(user, 'profile') and user.profile.is_verified:
                login(request, user)
                return redirect('home_page')
            else:
                return render(request, 'store/login.html', {'error': 'Email not verified'})
        return render(request, 'store/login.html', {'error': 'Invalid credentials'})

    return render(request, 'store/login.html')
 

# Forget Password View
def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(reverse('password_reset_confirm', args=[uid, token]))

            send_mail(
                'Leather Store - Password Reset Request',  # Updated subject with Leather Store
                f'Hello,\n\nYou requested a password reset for your Leather Store account.\n'
                f'Click the link below to reset your password:\n\n{reset_link}\n\n'
                f'If you did not request this, please ignore this email.\n\n'
                f'Thank you,\nLeather Store Team',  # Updated message with branding
                'noreply@leatherstore.com',  # Updated sender email
                [email],
            )
            return render(request, 'store/password_reset.html', {'message': 'Password reset link sent to your email'})

        return render(request, 'store/password_reset.html', {'error': 'Email not found'})
    return render(request, 'store/password_reset.html')

def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the UID from the base64-encoded URL parameter
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        user = None

    # Check if the user exists and if the token is valid
    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Ensure the passwords match
            if new_password != confirm_password:
                return render(request, 'store/password_reset_form.html', {'error': 'Passwords do not match', 'validlink': True, 'user': user})

            # Set the new password for the user
            user.set_password(new_password)
            user.save()

            # Redirect to the login page after password is reset
            return redirect('login')

        return render(request, 'store/password_reset_form.html', {'validlink': True, 'user': user})

    return render(request, 'store/password_reset_form.html', {'validlink': False, 'error': 'Invalid or expired link'})


def home_page(request):
    context = {
        'men_products': Product.objects.filter(category='Men Jackets'),
        'women_products': Product.objects.filter(category='Women Jackets'),
        'kids_products': Product.objects.filter(category='Kids Jackets'),
        'men_shorts': Product.objects.filter(category='Men Shorts'),
        'women_shorts': Product.objects.filter(category='Women Shorts'),
        'men_caps': Product.objects.filter(category='Men Caps'),
        'men_purse': Product.objects.filter(category='Men Purse'),
        'women_purse': Product.objects.filter(category='Women Purse'),
        'watch_straps': Product.objects.filter(category='Watch Straps'),
    }
    return render(request, 'Store/home_page.html', context)


# View to handle adding a product to the cart
# @login_required
@login_required
def add_to_cart(request, product_id):
    """Add a product to the cart and return JSON response."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Please log in to add items to cart'
            }, status=401)

        try:
            product = get_object_or_404(Product, id=product_id)
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                cart=cart,
                product=product,
                defaults={'price': product.discount_price if product.discount_price else product.price}
            )

            if not created:
                cart_item.quantity += 1
                cart_item.save()

            # Calculate updated cart info
            cart_count = CartItem.objects.filter(user=request.user).count()
            cart_total = sum(item.get_total_price() for item in CartItem.objects.filter(user=request.user))

            return JsonResponse({
                'status': 'success',
                'message': 'Product added to cart successfully',
                'cart_count': cart_count,
                'cart_total': float(cart_total),
                'cart_url': reverse('view_cart')
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


def product_list(request):
    return render(request, 'Store/product_list.html') 


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'Store/product_details.html', {'product': product})

# def checkout(request):
#     if request.method == 'POST':
#         try:
#             # Get cart items and verify cart is not empty
#             cart_items = CartItem.objects.filter(user=request.user)
#             if not cart_items.exists():
#                 messages.error(request, 'Your cart is empty')
#                 return redirect('view_cart')

#             # Calculate totals
#             subtotal = sum(item.get_total_price() for item in cart_items)
#             shipping_fee = Decimal('5.00')
#             tax_amount = subtotal * Decimal('0.10')
#             total_amount = subtotal + shipping_fee + tax_amount

#             # Create the order with all required fields
#             order = Order.objects.create(
#                 user=request.user,
#                 full_name=request.POST.get('full_name'),
#                 email=request.POST.get('email'),
#                 address=request.POST.get('address'),
#                 country=request.POST.get('country'),
#                 total_amount=total_amount,
#                 shipping_fee=shipping_fee,
#                 tax_amount=tax_amount,
#                 subtotal=subtotal,
#                 status='pending'
#             )

#             # Create order items
#             for cart_item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     product=cart_item.product,
#                     quantity=cart_item.quantity,
#                     price=cart_item.price,
#                     total=cart_item.get_total_price()
#                 )

#             # Clear user's cart after successful order creation
#             cart_items.delete()

#             # Save order ID in session for payment page
#             request.session['order_id'] = order.id

#             messages.success(request, 'Order created successfully!')
#             return redirect('payment_page')  # Redirect to payment page

#         except Exception as e:
#             messages.error(request, f'An error occurred: {str(e)}')
#             return redirect('checkout')

#     # GET request handling
#     cart_items = CartItem.objects.filter(user=request.user)
#     cart_subtotal = sum(item.get_total_price() for item in cart_items)
#     shipping_fee = Decimal('5.00')
#     tax_amount = cart_subtotal * Decimal('0.10')
#     final_total = cart_subtotal + shipping_fee + tax_amount

#     context = {
#         'cart_items': cart_items,
#         'cart_subtotal': cart_subtotal,
#         'shipping_fee': shipping_fee,
#         'tax_amount': tax_amount,
#         'final_total': final_total,
#     }
#     return render(request, 'Store/checkout.html', context)

def about_us(request):
    return render(request, 'Store/about_us.html')

def category_products(request, category_slug):
    category_name = category_slug.replace('-', ' ').title()
    products = Product.objects.filter(category=category_name)
    cart_count = get_cart_count(request)
    
    context = {
        'products': products,
        'category': category_slug,
        'cart_count': cart_count,
    }
    return render(request, 'Store/home_page.html', context)

def send_email(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        try:
            # Send email to store admin
            subject = f'New Contact Form Message from {name}'
            email_message = f'From: {name}\nEmail: {email}\n\nMessage:\n{message}'
            
            send_mail(
                subject,
                email_message,
                settings.EMAIL_HOST_USER,  # From email (your store's email)
                [settings.EMAIL_HOST_USER],  # To email (your store's email)
                fail_silently=False,
            )
            
            # Send confirmation email to user
            confirmation_subject = 'Thank you for contacting Leather Jacket Store'
            confirmation_message = f'''
            Dear {name},

            Thank you for contacting us. We have received your message and will get back to you shortly.

            Your message:
            {message}

            Best regards,
            Leather Jacket Store Team
            '''
            
            send_mail(
                confirmation_subject,
                confirmation_message,
                settings.EMAIL_HOST_USER,  # From email (your store's email)
                [email],  # To email (customer's email)
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, f'Failed to send message. Error: {str(e)}')
        
        return redirect('about_us')
    return redirect('about_us')

def send_contact_email(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        try:
            # Send email
            send_mail(
                f'Contact Form Message from {name}',
                f'From: {email}\n\nMessage:\n{message}',
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, 'Failed to send message. Please try again later.')
            
    return redirect('about_us')

@login_required
def order_success(request, order_id):
    """
    Display the order success page with the order ID
    """
    context = {
        'order_id': order_id
    }
    return render(request, 'Store/order_success.html', context)



def logout_view(request):
    """
    Log out the user and redirect to the home page
    """
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return HttpResponseRedirect(reverse('login'))

def shop_page(request):
    context = {
        'mens_jackets': Product.objects.filter(category='Men Jackets'),
        'womens_jackets': Product.objects.filter(category='Women Jackets'),
        'kids_jackets': Product.objects.filter(category='Kids Jackets'),
        'shorts': Product.objects.filter(category__in=['Men Shorts', 'Women Shorts']),
        'accessories': Product.objects.filter(
            category__in=['Men Caps', 'Men Purse', 'Women Purse', 'Watch Straps']
        ),
        'cart_count': get_cart_count(request),
    }
    return render(request, 'Store/shop_page.html', context)

def checkout(request):
    if request.method == 'POST':
        try:
            # Get cart items and calculate total
            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items.exists():
                messages.error(request, 'Your cart is empty')
                return redirect('checkout')

            subtotal = sum(item.get_total_price() for item in cart_items)
            shipping_fee = Decimal('5.00')
            tax_amount = subtotal * Decimal('0.10')
            total_amount = subtotal + shipping_fee + tax_amount

            # Create order
            order = Order.objects.create(
                user=request.user,
                customer_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                payment_method=request.POST.get('payment_method'),
                total_amount=total_amount,
                status='completed'  # Update status to completed
            )

            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.price
                )

            # Clear user's cart
            cart_items.delete()

            # Send confirmation email
            try:
                send_mail(
                    'Order Confirmation - Leather Store',
                    f'Thank you for your order! Your order ID is {order.id}.',
                    settings.EMAIL_HOST_USER,
                    [order.email],
                    fail_silently=True,
                )
            except Exception as e:
                # Log email error but don't stop the order process
                print(f"Email error: {str(e)}")

            return redirect('order_success', order_id=order.id)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('checkout')

    return redirect('checkout')

@login_required
def view_cart(request):
    USD_TO_PKR_RATE = 282  # Current conversion rate
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Convert all amounts to PKR
    subtotal = sum(item.get_total_price() for item in cart_items) * USD_TO_PKR_RATE
    shipping_fee = (Decimal('5.00') if cart_items else Decimal('0.00')) * USD_TO_PKR_RATE
    tax_amount = subtotal * Decimal('0.10')
    total = subtotal + shipping_fee + tax_amount
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'tax_amount': tax_amount,
        'total': total,
        'cart_count': get_cart_count(request),
        'USD_TO_PKR_RATE': USD_TO_PKR_RATE,  # Add conversion rate to context
    }
    return render(request, 'Store/view_cart.html', context)

@login_required
def update_cart(request, cart_item_id, action):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
        
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'remove':
            cart_item.delete()
        
        # Calculate new totals
        cart_items = CartItem.objects.filter(user=request.user)
        subtotal = sum(item.get_total_price() for item in cart_items)
        shipping_fee = Decimal('5.00') if cart_items else Decimal('0.00')
        tax_amount = subtotal * Decimal('0.10')
        total = subtotal + shipping_fee + tax_amount
        
        return JsonResponse({
            'status': 'success',
            'cart_count': cart_items.count(),
            'item_total': float(cart_item.get_total_price()) if not action == 'remove' else 0,
            'subtotal': float(subtotal),
            'shipping_fee': float(shipping_fee),
            'tax_amount': float(tax_amount),
            'total': float(total)
        })
    
    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cart item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)




# Payment View
def initiate_payment(request):
    if request.method == "POST":
        amount = request.POST.get("amount")

        # JazzCash API Parameters
        txn_ref_number = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        post_data = {
            "pp_Version": "1.1",
            "pp_TxnType": "MWALLET",
            "pp_Language": "EN",
            "pp_MerchantID": MERCHANT_ID,
            "pp_SubMerchantID": "",
            "pp_Password": PASSWORD,
            "pp_TxnRefNo": txn_ref_number,
            "pp_Amount": str(int(float(amount) * 100)),  # Convert amount to paisa
            "pp_TxnCurrency": "PKR",
            "pp_TxnDateTime": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "pp_BillReference": "Payment",
            "pp_Description": "Leather Store Payment",
            "pp_ReturnURL": RETURN_URL,
            "pp_SecureHash": "",  # This will be generated below
        }

        # Generate Secure Hash
        post_data["pp_SecureHash"] = generate_secure_hash(post_data)

        # JazzCash Payment URL
        jazzcash_url = "https://sandbox.jazzcash.com.pk/ApplicationAPI/API/Payment/DoTransaction"

        # Send Request to JazzCash API
        response = requests.post(jazzcash_url, data=post_data)
        response_data = response.json()

        if response_data["pp_ResponseCode"] == "000":
            return redirect(response_data["pp_TxnRefNo"])
        else:
            return JsonResponse({"error": response_data["pp_ResponseMessage"]}, status=400)

    return render(request, "store/payment.html")


def payment_response(request):
    if request.method == "POST":
        response_data = request.POST.dict()

        # Verify Secure Hash
        received_hash = response_data.pop("pp_SecureHash", None)
        generated_hash = generate_secure_hash(response_data)

        if received_hash == generated_hash and response_data.get("pp_ResponseCode") == "000":
            return render(request, "store/payment_success.html", {"data": response_data})
        else:
            return render(request, "store/payment_failed.html", {"error": "Transaction Failed!"})

    return redirect("home_page")