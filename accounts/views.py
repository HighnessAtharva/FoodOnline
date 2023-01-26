from django.shortcuts import render, redirect
from .forms import UserForm
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.contrib import messages

def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # user = form.save(commit=False)
            # user.set_password(form.cleaned_data['password'])
            
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            
            user.role = User.CUSTOMER
            user.save() 
            
            messages.success(request, f"Signup successful for user {username}!")            
            return redirect('registerUser')
        else:
            print(form.errors)
    else:
        form = UserForm()
    context = {'form': form}
    return render (request, 'accounts/registerUser.html', context)