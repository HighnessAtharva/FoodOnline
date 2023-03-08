from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendor.models import OpeningHour
from vendor.views import Vendor
from django.db.models import Prefetch
from .context_processors import get_cart_amount, get_cart_counter
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from datetime import timezone, date, datetime


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()

    context = {
        "vendors": vendors,
        "vendor_count": vendor_count,
    }
    return render(request, "marketplace/listings.html", context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch("fooditems", queryset=FoodItem.objects.filter(is_available=True))
    )

    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by(
        "day", "from_hour"
    )

    # check current days opening hours
    today = date.today()
    today = today.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        "vendor": vendor,
        "categories": categories,
        "cart_items": cart_items,
        "opening_hours": opening_hours,
        "current_opening_hours": current_opening_hours,
    }
    return render(request, "marketplace/vendor_detail.html", context)


def add_to_cart(request, food_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        return JsonResponse({"status": "Failed", "message": "Invalid request"})
    try:
        fooditem = FoodItem.objects.get(id=food_id)
        try:
            chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
            chkCart.quantity += 1
            chkCart.save()
            return JsonResponse(
                {
                    "status": "Success",
                    "message": "Increased the cart quantity",
                    "cart_counter": get_cart_counter(request),
                    "qty": chkCart.quantity,
                    "cart_amount": get_cart_amount(request),
                }
            )
        except Exception:
            chkCart = Cart.objects.create(
                user=request.user, fooditem=fooditem, quantity=1
            )
            return JsonResponse(
                {
                    "status": "Success",
                    "message": "Added the food to the cart",
                    "cart_counter": get_cart_counter(request),
                    "qty": chkCart.quantity,
                    "cart_amount": get_cart_amount(request),
                }
            )
    except Exception:
        return JsonResponse(
            {"status": "Failed", "message": "This food does not exist!"}
        )


def decrease_cart(request, food_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "login_required", "message": "Please login to continue"}
        )
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        return JsonResponse({"status": "Failed", "message": "Invalid request"})
    try:
        fooditem = FoodItem.objects.get(id=food_id)
        try:
            chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
            if chkCart.quantity > 1:
                chkCart.quantity -= 1
                chkCart.save()
            else:
                chkCart.delete()
                chkCart.quantity = 0
            return JsonResponse(
                {
                    "status": "Success",
                    "message": "Increased the cart quantity",
                    "cart_counter": get_cart_counter(request),
                    "qty": chkCart.quantity,
                    "cart_amount": get_cart_amount(request),
                }
            )
        except Exception:
            return JsonResponse(
                {"status": "Failed", "message": "Item quantity is already zero."}
            )
    except Exception:
        return JsonResponse(
            {"status": "Failed", "message": "This food does not exist!"}
        )


@login_required(login_url="login")
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    context = {
        "cart_items": cart_items,
    }
    return render(request, "marketplace/cart.html", context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") != "XMLHttpRequest":
            return JsonResponse({"status": "Failed", "message": "Invalid request"})
        try:
            if cart_item := Cart.objects.get(user=request.user, id=cart_id):
                cart_item.delete()
                return JsonResponse(
                    {
                        "status": "Success",
                        "message": "Item removed from the cart",
                        "cart_counter": get_cart_counter(request),
                        "cart_amount": get_cart_amount(request),
                    }
                )
        except Exception:
            return JsonResponse(
                {"status": "Failed", "message": "Item does not exist in the cart"}
            )


def search(request):

    if "address" not in request.GET:
        return redirect("marketplace")
    address = request.GET.get("address")
    latitude = request.GET.get("lat")
    longitude = request.GET.get("lng")
    radius = request.GET.get("radius")
    keyword = request.GET.get("keyword")

    # get vendor ids that the food items belong to that match the keyword
    fetch_vendors_by_fooditems = FoodItem.objects.filter(
        food_title__icontains=keyword, is_available=True
    ).values_list("vendor", flat=True)

    vendors = Vendor.objects.filter(
        Q(id__in=fetch_vendors_by_fooditems)
        | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
    )

    if latitude and longitude and radius:
        pnt = GEOSGeometry(f"POINT({longitude} {latitude})", srid=4326)

        vendors = (
            Vendor.objects.filter(
                Q(id__in=fetch_vendors_by_fooditems)
                | Q(
                    vendor_name__icontains=keyword,
                    is_approved=True,
                    user__is_active=True,
                ),
                user_profile__location__distance_lte=(pnt, D(km=radius)),
            )
            .annotate(distance=Distance("user_profile__location", pnt))
            .order_by("distance")
        )

        for v in vendors:
            v.kms = round(v.distance.km, 1)

    vendors_count = vendors.count()
    context = {
        "vendors": vendors,
        "vendors_count": vendors_count,
        "source_location": address,
    }
    return render(request, "marketplace/listings.html", context)
