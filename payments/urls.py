from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('mobile/<int:payment_id>/', views.mobile_payment, name='mobile_payment'),
    path('online/<int:payment_id>/', views.online_payment, name='online_payment'),
    path('card/<int:payment_id>/', views.card_payment, name='card_payment'),
]
