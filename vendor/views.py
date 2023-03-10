from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodItemForm
from .forms import VendorForm, OpeningHourForm
from .models import OpeningHour, Vendor
from django.template.defaultfilters import slugify



def get_vendor(request):
    return Vendor.objects.get(user=request.user)



@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendorProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect("vendorProfile")
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
        
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        "profile_form": profile_form,
        "vendor_form": vendor_form,
        "profile": profile,
        "vendor": vendor,
    }
    return render(request, "vendor/vendorProfile.html", context)



@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def menuBuilder(request):
    vendor= get_vendor(request)
    categories=Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {'categories': categories,}
    return render(request, "vendor/menuBuilder.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def fooditemsByCategory(request, pk=None):
    vendor= get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    food_items = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {'food_items': food_items,
                'category': category,
            }
    print(food_items)
    return render(request, "vendor/fooditemsByCategory.html", context)


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def addCategory(request):
    if request.method == "POST":
        form=CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name'].capitalize()
            category=form.save(commit=False)
            category.vendor= get_vendor(request)
            category.save()
            category.slug = f'{slugify(category_name)}-{str(category.id)}'
            category.save()

            messages.success(request, f"Category {category_name} added successfully")
            return redirect("menuBuilder")
        else:
            messages.error(request, "That category already exists.")
    else:
        form=CategoryForm()
    context= {
        'form': form,
    }
    return render(request, "vendor/addCategory.html", context)



@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def editCategory(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form=CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category=form.save(commit=False)
            category.vendor= get_vendor(request)
            category.slug = slugify(category_name)
            form.save()

            messages.success(request, f"Category {category_name} updated successfully")
            return redirect("menuBuilder")
        else:
            messages.error(request, "That category already exists.")
    else:
        form=CategoryForm(instance=category)
    context= {
        'form': form,
        'category': category,
    }
    return render(request, "vendor/editCategory.html", context)




@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def deleteCategory(request, pk=None):
    category= get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, f"Category {category.category_name} deleted successfully")
    return redirect("menuBuilder")




@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def addFood(request):
    if request.method == "POST":
        form=FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food=form.save(commit=False)
            food.vendor= get_vendor(request)
            food.slug = slugify(food_title)
            form.save()

            messages.success(request, f"Food item {food_title} added successfully")
            return redirect("fooditemsByCategory", pk=food.category.pk)
        else:
            messages.error(request, "That category already exists.")
    else:
        form=FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    
    context= {
            'form': form,
        }
    return render(request, "vendor/addFood.html", context) 


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def editFood(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == "POST":
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food=form.save(commit=False)
            food.vendor= get_vendor(request)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, f"Food item {foodtitle} updated successfully")
            return redirect("fooditemsByCategory", pk=food.category.id)
        else:
            messages.error(request, f"{form.errors}")
            
    else:
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
        
    context= {
            'form': form,
            'food': food,
            }
    return render(request, "vendor/editFood.html", context) 


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def deleteFood(request, pk=None):
    food= get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, f"Food item {food.food_title} deleted successfully")
    return redirect("fooditemsByCategory", pk=food.category.id) 



def openingHours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()

    context = {'form':form, 
               'opening_hours': opening_hours
            }
    return render(request, "vendor/openingHours.html", context)


def addOpeningHours(request):
    # handle data and save to db
    if not request.user.is_authenticated:
        return
    if request.headers.get("x-requested-with") == "XMLHttpRequest" and request.method == "POST":
        day = request.POST.get("day")
        from_hour = request.POST.get("from_hour")
        to_hour = request.POST.get("to_hour")
        is_closed = request.POST.get("is_closed")
        print(day, from_hour, to_hour, is_closed)
        try:
            if hour := OpeningHour.objects.create(
                vendor=get_vendor(request),
                day=day,
                from_hour=from_hour,
                to_hour=to_hour,
                is_closed=is_closed,
            ):
                day = OpeningHour.objects.get(id=hour.id)
                if day.is_closed:
                    response = {'status': 'success', 'id': hour.id, 'day':day.get_day_display(), 'is_closed':'Closed'}
                else:
                    response = {'status': 'success', 'id': hour.id, 'day':day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': hour.to_hour}

            return JsonResponse(response)

        except IntegrityError as e:
            response = {'status': 'failed', 'message': 'Hours already exist for this day.'}
            return JsonResponse(response)

    else:
        HttpResponse("Invalid Request")    
            
def removeOpeningHours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({
                'status': 'success',
                'id': pk,
            })
            
        else:
            HttpResponse("Invalid Request")  