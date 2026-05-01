from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

# Custom logout view that accepts GET requests
def custom_logout(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.success(request, 'You have been successfully logged out!')
        return redirect('login')
    return redirect('dashboard')