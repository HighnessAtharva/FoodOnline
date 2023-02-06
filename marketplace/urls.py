from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.marketplace, name="marketplace"),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendorDetail'),
    path("add_to_cart/<int:food_id>/", views.add_to_cart, name="addToCart"),
    path("decrease_card/<int:food_id>/", views.decrease_cart, name="decreaseCart"),
    path("delete_cart/<int:cart_id>/", views.delete_cart, name="deleteCart"),
   
]