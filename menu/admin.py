from django.contrib import admin
from .models import Category, FoodItem

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('category_name',)}
    list_display = ('category_name', 'vendor', 'description', 'updated_at')
    # put __ because vendor is a foreign key and the name of the column is vendor_name. So refer to the vendor_name column in the vendor table
    search_fields = ('category_name', 'vendor__vendor_name')
    
class FoodAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('food_title',)}
    list_display = ('food_title', 'category', 'price', 'vendor', 'updated_at')
    search_fields = ('food_title', 'category__category_name', 'vendor__vendor_name', 'price')
    list_filter = ('is_available', )
    
admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodAdmin)

