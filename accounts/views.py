from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode

from vendor.forms import VendorForm
from vendor.models import Vendor

from .forms import UserForm
from .models import User, UserProfile
from .utils import detectUser, send_verification_email


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully")
        return redirect("myAccount")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("registerUser")


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("dashboard")

    elif request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            # user = form.save(commit=False)
            # user.set_password(form.cleaned_data['password'])

            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"].lower()
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )

            user.role = User.CUSTOMER
            user.save()

            # send verification email
            mail_subject = "Activate your account"
            mail_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, mail_template)

            messages.success(request, f"Signup successful for user {username}!")
            return redirect("registerUser")
        else:
            print(form.errors)
    else:
        form = UserForm()
    context = {"form": form}
    return render(request, "accounts/registerUser.html", context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("dashboard")

    elif request.method == "POST":
        form = UserForm(request.POST)
        vendorForm = VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendorForm.is_valid():
            # user = form.save(commit=False)
            # user.set_password(form.cleaned_data['password'])

            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"].lower()
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )

            user.role = User.VENDOR
            user.save()

            # send verification email
            mail_subject = "Activate your account"
            mail_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, mail_template)

            vendor = vendorForm.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            messages.success(
                request, f"Signup successful for {username}! Stand by for approval."
            )
            return redirect("registerVendor")
        else:
            print(form.errors)

    else:
        form = UserForm()
        vendorForm = VendorForm()
    context = {"form": form, "vendorForm": vendorForm}
    return render(request, "accounts/registerVendor.html", context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("myAccount")

    elif request.method == "POST":
        email = request.POST["email"].lower()
        password = request.POST["password"]
        if user := auth.authenticate(email=email, password=password):
            auth.login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect("myAccount")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.info(request, "Logged out successfully!")
    return render(request, "accounts/login.html")


@login_required(login_url="login")
def myAccount(request):
    user = request.user
    redirectURL = detectUser(user)
    return redirect(redirectURL)


# restrict vendor from accessing customers page
def check_role_vendor(user):
    if user.role == User.VENDOR:
        return True
    else:
        raise PermissionDenied


# restrict customer from accessing vendors page
def check_role_customer(user):
    if user.role == User.CUSTOMER:
        return True
    else:
        raise PermissionDenied


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customerDashboard(request):
    return render(request, "accounts/customerDashboard.html")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, "accounts/vendorDashboard.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"].lower()
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__iexact=email)
            mail_subject = "Reset your password"
            mail_template = "accounts/emails/reset_password_email.html"
            send_verification_email(request, user, mail_subject, mail_template)
            messages.success(request, f"Password reset email has been sent to {email}")
            return redirect("login")
        else:
            messages.error(request, "Account does not exist")
            return redirect("forgot_password")

    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.info(request, "Please reset your password")
        return redirect("reset_password")
    else:
        messages.error(request, "The link has expired")
        return redirect("myAccount")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset success")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("reset_password")
    return render(request, "accounts/reset_password.html")
