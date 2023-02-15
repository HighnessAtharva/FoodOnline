from django.urls import include, path
from accounts import views as accounts_views
from . import views

urlpatterns = [
    path("", accounts_views.customerDashboard, name="customer"),
    path("profile/", views.customerProfile, name="customerProfile"),
]
