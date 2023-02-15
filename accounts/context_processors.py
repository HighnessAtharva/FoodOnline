from django.conf import settings
from accounts.models import UserProfile
from vendor.models import Vendor


def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Exception:
        vendor = None
    return dict(vendor=vendor)


def get_user_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except Exception:
        user_profile = None
    return dict(user_profile=user_profile)

def get_tomtom_api_key(request):
    return {'TOMTOM_API_KEY': settings.TOMTOM_API_KEY}