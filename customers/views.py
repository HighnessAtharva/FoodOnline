from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile
from django.contrib import messages


@login_required(login_url="login")
def customerProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_info_form.is_valid():
            profile_form.save()
            user_info_form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect("customerProfile")
        else:
            print(profile_form.errors)
            print(user_info_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_info_form = UserInfoForm(instance=request.user)
    
    context= {
        "profile_form": profile_form,
        "user_form": user_info_form,
        "profile": profile,
    }
    
    return render(request, "customers/customerProfile.html", context)