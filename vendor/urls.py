from django.urls import include, path

from accounts import views as accounts_views

from . import views

urlpatterns = [
    path("", accounts_views.vendorDashboard, name="vendor"),
    path("profile/", views.vendorProfile, name="vendorProfile"),
    path('menu-builder/', views.menuBuilder, name="menuBuilder"),
    path('menu-builder/category/<int:pk>/', views.fooditemsByCategory, name="fooditemsByCategory"),

    # CATEGORY CRUD
    path('menu-builder/category/add/', views.addCategory, name="addCategory"),
    path("menu-builder/category/edit/<int:pk>/", views.editCategory, name="editCategory"),
    path("menu-builder/category/delete/<int:pk>/", views.deleteCategory, name="deleteCategory"),
    
    # FOOD CRUD
    path('menu-builder/food/add/', views.addFood, name="addFood"),   
    path("menu-builder/food/edit/<int:pk>/", views.editFood, name="editFood"), 
    path("menu-builder/food/delete/<int:pk>/", views.deleteFood, name="deleteFood"),

    # OPENING HOURS
    path('opening-hours/', views.openingHours, name="openingHours"),
    path('opening-hours/add/', views.addOpeningHours, name="addOpeningHours"),
    path('opening-hours/remove/<int:pk>/', views.removeOpeningHours, name="removeOpeningHours"),
]
 