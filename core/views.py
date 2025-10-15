from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import UserProfile, Booking, ChatMessage
import json

def index(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
            if profile.role == 'customer':
                return redirect('customer_dashboard')
            elif profile.role == 'delivery':
                return redirect('delivery_dashboard')
            elif profile.role == 'admin':
                return redirect('admin_dashboard')
        except:
            pass
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        otp = request.POST.get('otp')
        role = request.POST.get('role', 'customer')
        
        # Static OTP validation
        if otp != '1234':
            return JsonResponse({'success': False, 'error': 'Invalid OTP'})
        
        try:
            profile = UserProfile.objects.get(mobile=mobile)
            user = profile.user
            
            if profile.role != role:
                return JsonResponse({'success': False, 'error': 'Invalid role for this mobile number'})
        except UserProfile.DoesNotExist:
            # Create new user for customer role
            if role == 'customer':
                username = f"user_{mobile}"
                user = User.objects.create_user(username=username)
                profile = UserProfile.objects.create(
                    user=user,
                    role=role,
                    mobile=mobile
                )
            else:
                return JsonResponse({'success': False, 'error': 'User not found'})
        
        login(request, user)
        
        redirect_url = {
            'customer': '/customer/',
            'delivery': '/delivery/',
            'admin': '/admin-dashboard/'
        }.get(role, '/')
        
        return JsonResponse({'success': True, 'redirect': redirect_url})
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def customer_dashboard(request):
    profile = request.user.userprofile
    if profile.role != 'customer':
        return redirect('index')
    
    bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'customer_dashboard.html', {'bookings': bookings})

@login_required
@require_POST
def create_booking(request):
    data = json.loads(request.body)
    
    booking = Booking.objects.create(
        customer=request.user,
        restaurant_name=data['restaurant_name'],
        delivery_address=data['delivery_address'],
        items=data['items'],
        total_amount=data['total_amount']
    )
    
    return JsonResponse({
        'success': True,
        'booking_id': booking.id,
        'message': 'Booking created successfully'
    })

@login_required
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    
    if booking.status in ['pending', 'assigned']:
        booking.status = 'cancelled'
        booking.save()
        return JsonResponse({'success': True, 'message': 'Booking cancelled'})
    
    return JsonResponse({'success': False, 'error': 'Cannot cancel this booking'})

@login_required
def delivery_dashboard(request):
    profile = request.user.userprofile
    if profile.role != 'delivery':
        return redirect('index')
    
    bookings = Booking.objects.filter(delivery_partner=request.user).exclude(status='delivered').order_by('-created_at')
    return render(request, 'delivery_dashboard.html', {'bookings': bookings})

@login_required
@require_POST
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, delivery_partner=request.user)
    new_status = request.POST.get('status')
    
    valid_transitions = {
        'assigned': 'started',
        'started': 'reached',
        'reached': 'collected',
        'collected': 'delivered'
    }
    
    if booking.status in valid_transitions and valid_transitions[booking.status] == new_status:
        booking.status = new_status
        booking.save()
        return JsonResponse({'success': True, 'message': 'Status updated'})
    
    return JsonResponse({'success': False, 'error': 'Invalid status transition'})

@login_required
def admin_dashboard(request):
    profile = request.user.userprofile
    if profile.role != 'admin':
        return redirect('index')
    
    bookings = Booking.objects.all().order_by('-created_at')
    delivery_partners = User.objects.filter(userprofile__role='delivery')
    
    return render(request, 'admin_dashboard.html', {
        'bookings': bookings,
        'delivery_partners': delivery_partners
    })

@login_required
@require_POST
def assign_delivery_partner(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    partner_id = request.POST.get('partner_id')
    print(partner_id)
    
    partner = get_object_or_404(User, id=partner_id, userprofile__role='delivery')
    booking.delivery_partner = partner
    booking.status = 'assigned'
    booking.save()
    
    return JsonResponse({'success': True, 'message': 'Delivery partner assigned'})

@login_required
def chat_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user is authorized to access this chat
    if request.user != booking.customer and request.user != booking.delivery_partner:
        return redirect('index')
    
    messages = ChatMessage.objects.filter(booking=booking)
    
    return render(request, 'chat.html', {
        'booking': booking,
        'messages': messages
    })

@login_required
def get_chat_messages(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    messages = ChatMessage.objects.filter(booking=booking)
    
    data = [{
        'sender': msg.sender.username,
        'message': msg.message,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'is_own': msg.sender == request.user
    } for msg in messages]
    
    return JsonResponse({'messages': data})