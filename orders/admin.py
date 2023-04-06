from django.contrib import admin
from .models import Order, OrderedFood, Payment
# Register your models here.

admin.site.register(Order)
admin.site.register(OrderedFood)
admin.site.register(Payment)

