from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendor.views import Vendor
from django.db.models import Prefetch

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    
    context={
        'vendors': vendors, 
        'vendor_count': vendor_count,
    }
    return render(request, "marketplace/listings.html", context)


def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch('fooditems', 
                 queryset=FoodItem.objects.filter(is_available=True)
                 )
    )
    
    if request.user.is_authenticated:
        cart_items= Cart.objects.filter(user=request.user)
    else:
        cart_items = None
        
    
    context={
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, "marketplace/vendor_detail.html", context)


def add_to_cart(request, food_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
    try:
        fooditem = FoodItem.objects.get(id=food_id)
        try:
            chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
            chkCart.quantity += 1
            chkCart.save()
            return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity'})
        except Exception:
            chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
            return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart'})
    except Exception:
        return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
