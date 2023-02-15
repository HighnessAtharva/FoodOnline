from .models import Cart, Tax
from menu.models import FoodItem


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            if cart_items := Cart.objects.filter(user=request.user):
                for item in cart_items:
                    cart_count += item.quantity
            else:
                cart_count = 0
        except Exception:
            cart_count = 0
    return {"cart_count": cart_count}


def get_cart_amount(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += fooditem.price * item.quantity

        get_tax = Tax.objects.filter(is_active=True)
        
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage / 100) * subtotal,2)
            tax_dict[tax_type] = {str(tax_percentage): tax_amount}

        
        for key in tax_dict.values():
            for x in key.values():
                tax += x
        
        
        
        grand_total = subtotal + tax
    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
