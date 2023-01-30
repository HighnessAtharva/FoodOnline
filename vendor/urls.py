from django.urls import path, include

from . import views
from accounts import views as accounts_views

urlpatterns = [
    path('', accounts_views.vendorDashboard, name='vendor'),
    path('profile/', views.vendorProfile, name='vendorProfile'),
]