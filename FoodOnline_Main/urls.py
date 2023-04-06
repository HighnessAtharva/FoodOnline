from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from marketplace import views as marketplace_views

from . import views

urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("", include("accounts.urls")),
    path("marketplace/", include("marketplace.urls")),
    path("cart/", marketplace_views.cart, name="cart"),
    path("search/", marketplace_views.search, name="search"),
    path("checkout/", marketplace_views.checkout, name="checkout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
