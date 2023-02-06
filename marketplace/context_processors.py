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

def get_cart_amount(request):
    subtotal=0
    tax=0
    grand_total=0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal+= (fooditem.price * item.quantity)
        
        grand_total = subtotal + tax
    print(subtotal)
    print(grand_total)
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total)