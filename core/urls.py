from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Customer URLs
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/booking/create/', views.create_booking, name='create_booking'),
    path('customer/booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Delivery Partner URLs
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/booking/<int:booking_id>/update/', views.update_booking_status, name='update_booking_status'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('booking/<int:booking_id>/assign/', views.assign_delivery_partner, name='assign_delivery_partner'),
    
    # Chat URLs
    path('chat/<int:booking_id>/', views.chat_view, name='chat'),
    path('chat/<int:booking_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
]