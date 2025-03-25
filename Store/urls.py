from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart/<int:cart_item_id>/<str:action>/', views.update_cart, name='update_cart'),  
    path('checkout/', views.checkout, name='checkout'),
    path('about/', views.about_us, name='about_us'),
    path('send-contact-email/', views.send_contact_email, name='send_contact_email'),
    path('payment/', views.payment_page, name='payment_page'),
    path('category/<str:category_slug>/', views.category_products, name='category_products'),
    path('order-success/', views.order_success, name='order_success'),
    path('order-success/<str:order_id>/', views.order_success, name='order_success'),
    path('logout/', views.logout_view, name='logout'),
    path('shop/', views.shop_page, name='shop_page'),
    path('register/', views.register_page, name='register'), 
    path('login/', views.login_view, name='login'),  # Changed from 'login_view' to 'login'
    path('process-payment/', views.process_payment, name='process_payment'),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('verify/', views.verify_email, name='verify_email'),
]
