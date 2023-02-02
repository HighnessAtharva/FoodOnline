from django.conf import settings
from vendor.models import Vendor


def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Exception:
        vendor = None
    return dict(vendor=vendor)


def get_tomtom_api_key(request):
    return {'TOMTOM_API_KEY': settings.TOMTOM_API_KEY}