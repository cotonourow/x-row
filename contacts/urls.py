from django.urls import path
from . import views

urlpatterns = [
    # CONTACT (HTML)
    path('', views.contact_list, name='contact_list'),
    path('search/', views.search_contacts),

    # AUTH
    path('auth/register/', views.register_user),
    path('auth/login/', views.login_user),

    # WORKERS API
    path('workers/search/', views.search_workers),
    path('workers/stats/', views.get_worker_stats),
    path('workers/<int:worker_id>/', views.get_worker_detail),
]