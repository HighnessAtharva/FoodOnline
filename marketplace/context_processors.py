from .models import Cart
from menu.models import FoodItem


def get_cart_counter(request):
    cart_count=0
    if request.user.is_authenticated:
        try:
            if cart_items := Cart.objects.filter(user=request.user):
                for item in cart_items:
                    cart_count += item.quantity
            else:
                cart_count=0
        except Exception:
            cart_count=0
    return {'cart_count': cart_count}