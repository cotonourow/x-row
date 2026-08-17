from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Contact, Worker

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings


# ==================== CONTACT (HTML SYSTEM) ====================

def contact_list(request):
    contacts = Contact.objects.all().order_by('name')
    return render(request, 'contacts/contact_list.html', {'contacts': contacts})


def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, 'contacts/contact_detail.html', {'contact': contact})


def contact_create(request):
    if request.method == 'POST':
        Contact.objects.create(
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            profession=request.POST.get('profession')
        )
        messages.success(request, "Contact created successfully!")
        return redirect('contact_list')

    return render(request, 'contacts/contact_form.html')


def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'POST':
        contact.name = request.POST.get('name')
        contact.phone = request.POST.get('phone')
        contact.profession = request.POST.get('profession')
        contact.save()

        messages.success(request, "Contact updated successfully!")
        return redirect('contact_list')

    return render(request, 'contacts/contact_form.html', {'contact': contact})


def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'POST':
        contact.delete()
        messages.success(request, "Contact deleted successfully!")
        return redirect('contact_list')

    return render(request, 'contacts/contact_confirm_delete.html', {'contact': contact})


# ==================== CONTACT SEARCH ====================

def search_contacts(request):
    query = request.GET.get('q', '').strip()
    contacts = []

    if query:
        contacts = Contact.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(profession__icontains=query)
        ).order_by('name')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'count': contacts.count(),
                'contacts': list(contacts.values('id', 'name', 'phone', 'profession'))
            })

    return render(request, 'contacts/search_results.html', {
        'contacts': contacts,
        'query': query
    })


def get_professions(request):
    professions = Contact.objects.values_list('profession', flat=True).distinct()
    return JsonResponse({'professions': list(professions)})


# ==================== AUTH SYSTEM ====================

def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = (request.data.get("username") or "").strip()
    password = (request.data.get("password") or "").strip()

    if not username or not password:
        return Response({"error": "Username and password required"}, status=400)

    if len(password) < 6:
        return Response({"error": "Password too short"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, status=400)

    user = User.objects.create_user(username=username, password=password)

    return Response({
        "message": "User created",
        "user": {"id": user.id, "username": user.username},
        **get_tokens(user)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = (request.data.get("username") or "").strip()
    password = (request.data.get("password") or "").strip()

    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid credentials"}, status=401)

    return Response({
        "message": "Login successful",
        "user": {"id": user.id, "username": user.username},
        **get_tokens(user)
    })


# ==================== WORKER SYSTEM ====================

SKILL_DISPLAY_MAP = {
    'engineer': 'Engineer',
    'electrician': 'Electrician',
    'painter': 'Painter',
    'mason': 'Bricklayer / Mason',
    'welder': 'Welder',
    'carpenter': 'Carpenter',
    'labourer': 'Laborer',
}


def get_skill_display(skill):
    return SKILL_DISPLAY_MAP.get(skill, skill.replace("_", " ").title())


# 🔒 PROTECTED
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_worker_stats(request):
    stats = Worker.objects.values('skill').annotate(
        count=Count('id'),
        avg_rating=Avg('rating')
    )

    result = {}
    for item in stats:
        result[get_skill_display(item['skill'])] = {
            "count": item["count"],
            "avg_rating": round(item["avg_rating"] or 0, 1),
        }

    return Response({"stats": result})


# 🔒 PROTECTED + PAGINATION
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_workers(request):
    skill = request.GET.get("skill", "").strip()
    location = request.GET.get("location", "").strip()
    q = request.GET.get("q", "").strip()

    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 20))

    workers = Worker.objects.all()

    if q:
        workers = workers.filter(
            Q(name__icontains=q) |
            Q(skill__icontains=q) |
            Q(location__icontains=q)
        )

    if skill:
        workers = workers.filter(skill=skill)

    if location:
        workers = workers.filter(location__icontains=location)

    total = workers.count()

    start = (page - 1) * per_page
    end = start + per_page

    workers = workers.order_by("-rating")[start:end]

    data = list(workers.values(
        "id", "name", "skill", "location", "phone",
        "experience_years", "rating", "is_available"
    ))

    for w in data:
        w["skill_display"] = get_skill_display(w["skill"])

    return Response({
        "results": data,
        "count": total,
        "page": page,
        "has_more": end < total
    })


# 🔒 PROTECTED
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_worker_detail(request, worker_id):
    try:
        w = Worker.objects.get(id=worker_id)

        return Response({
            "id": w.id,
            "name": w.name,
            "skill": w.skill,
            "skill_display": get_skill_display(w.skill),
            "location": w.location,
            "phone": w.phone,
            "rating": w.rating,
            "experience": w.experience_years,
            "available": w.is_available
        })

    except Worker.DoesNotExist:
        return Response({"error": "Worker not found"}, status=404)


# ==================== PASSWORD RESET ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    OPTION B: Display reset link directly on screen (no email needed)
    """
    email = request.data.get("email", "").strip()
    if not email:
        return Response({"error": "Email is required"}, status=400)

    try:
        # Try to find the user
        user = User.objects.get(email=email)
        user_found = True
    except User.DoesNotExist:
        # User not found — don't reveal this, generate dummy token for security
        user_found = False
        user = None

    # Generate token and uid (works for both real and dummy users)
    if user_found:
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
    else:
        # For non-existent emails, create a dummy token
        token = PasswordResetTokenGenerator().make_token(User())
        uid = urlsafe_base64_encode(force_bytes("0"))

    reset_url = f"https://cotonourow.com/reset-password?uid={uid}&token={token}"

    # Try to send email if user exists (will fail silently if email not configured)
    if user_found:
        try:
            send_mail(
                subject="Password Reset - Cotonourow",
                message=f"Click this link to reset your password:\n\n{reset_url}\n\nIf you didn't request this, ignore this email.",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cotonourow.com'),
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass

    # OPTION B: Always return the reset_url so users can click it directly
    return Response({
        "success": True,
        "message": "If this email exists, a reset link has been sent.",
        "data": {
            "reset_url": reset_url,
            "uid": uid,
            "token": token
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """
    Validate reset link and update password
    """
    uid = request.data.get("uid", "")
    token = request.data.get("token", "")
    new_password = request.data.get("new_password", "")

    if not all([uid, token, new_password]):
        return Response({"error": "All fields are required"}, status=400)
    
    if len(new_password) < 6:
        return Response({"error": "Password must be at least 6 characters"}, status=400)

    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({
            "success": True,
            "message": "Password reset successfully. You can now log in."
        })
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Invalid reset link"}, status=400)
