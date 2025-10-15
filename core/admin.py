from django.contrib import admin
from .models import UserProfile, Booking, ChatMessage

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'mobile']
    list_filter = ['role']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'delivery_partner', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['booking', 'sender', 'message', 'timestamp']
    list_filter = ['timestamp']