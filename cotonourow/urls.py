from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("X-ROW Backend is LIVE 🚀")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contacts/', include('contacts.urls')),
    path('', home),  # 👈 ADD THIS LINE
]