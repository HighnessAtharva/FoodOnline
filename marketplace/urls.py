from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.marketplace, name="marketplace"),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendorDetail'),
    path("add_to_cart/<int:food_id>/", views.add_to_cart, name="addToCart"),
]