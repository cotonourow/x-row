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